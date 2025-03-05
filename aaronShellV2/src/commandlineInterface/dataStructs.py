from abc import ABC,abstractmethod
import asyncio

import os
from subprocess import Popen
from threading import Semaphore, RLock, Thread
from typing import Any, List

from asyncssh import SSHClientProcess


class CommandLinkerObject:

    def __init__(self) -> None:
        self.objectLock = RLock()
        self.commandOutputList:List["CommandOutput"] = []
        self.hasFatalError = False
        self.waitingForResult = False
        self.exeption = None
        self.resultSemaphore = Semaphore(value=0)


    def addCommandOutput(self,commandOutput:"CommandOutput") -> None:
        with self.objectLock:

            if self.waitingForResult:
                err = RuntimeError("Can not add new commandActors when there is a thread already waiting for the result")
                self.signalFatalError(err)
                return

            if self.exeption is not None:
                commandOutput.kill()
                return
            
            self.commandOutputList.append(commandOutput)
            return


    def __killAll(self) -> None:
        for commandOutput in self.commandOutputList:
            commandOutput.kill()
    
    def waitForResutAvailable(self) -> None:
        with self.objectLock:
            self.waitingForResult = True

        print(f"waiting for {len(self.commandOutputList)}")
        for _ in range(len(self.commandOutputList)):
            self.resultSemaphore.acquire(blocking=True,timeout=None)
    
    def signalActorHasFinshed(self):
        with self.objectLock:
            print("finished")
            self.resultSemaphore.release(1)
    
    def signalFatalError(self,exeption:Exception|None = None):
        with self.objectLock:
            self.exeption = exeption
            self.__killAll()
            self.resultSemaphore.release(len(self.commandOutputList))



class CommandOutput(ABC):

    def __init__(self,commandLinkerObject:CommandLinkerObject|None=None) -> None:
        #if there is no linker object provided we should create it here 
        if commandLinkerObject is None:
            commandLinkerObject = CommandLinkerObject()
        commandLinkerObject.addCommandOutput(self)

        self.commandLinkerObject = commandLinkerObject
        self.returnCode = None
    
    """signal that the actor responsible of this Output is finished with a return code"""
    def succeed(self,retcode:int):
        self.commandLinkerObject.signalActorHasFinshed()
        self.returnCode=retcode
    
    """signal that the actor responsible of this Output has had an error"""
    def fatalError(self,retcode:int,exeption:Exception|None = None):
        self.commandLinkerObject.signalFatalError(exeption)
        self.returnCode=retcode

    #helper function to thread clearing out the stdErr buffer of the final output
    async def _voidErrFunc(self):
        while True:
            data = await self.readErr(1)
            if not data:
                break
    

    """wait untill all linked actors are finished and return the return code and string output of the last one"""
    async def getOutPutAndReturnCode(self) -> tuple[int,str]:

        # voidStdErr = Thread(target = lambda: asyncio.run(self._voidErrFunc()))
        # voidStdErr.start()
        output = ""
        while True:
            data = await self.readOut(1)
            if not data:
                break
            output += data.decode('utf-8')
        print(f"output: {output}")
        self.commandLinkerObject.waitForResutAvailable()
        if self.commandLinkerObject.exeption is not None:
            raise self.commandLinkerObject.exeption
        
        if self.returnCode is None:
            raise RuntimeError("If the result is available this should be impossible -> report as bug")
        
        return (self.returnCode,output)
    
    """kill the actor responsible of this Output"""
    @abstractmethod
    def kill(self) -> None:
        pass

    """interface to communicate with command output on all platforms, functions are async due to compatibility"""    
    @abstractmethod
    async def readOut(self, amount_of_bytes:int) -> bytes:
        """reads at most amount_of_bytes from the available stdout"""
        pass
    
    @abstractmethod
    async def readErr(self, amount_of_bytes:int) -> bytes:
        """reads at most amount_of_bytes from the available stderr"""
        pass
    
    """get a an objet that is compatible as File descriptor for the stdout of this output"""
    @abstractmethod
    def getReaderFdOut(self) -> Any:
        pass
    
    """get a an objet that is compatible as File descriptor for the stderr of this output"""
    @abstractmethod
    def getReaderFdErr(self) -> Any:
        pass
        


class LocalCommandOutput(CommandOutput):
    """implementation of the interface using standard IO interactions,
    this implementation is specificaly to interact with the subprocesses module
    see CommandOutput class for function documentation"""
    def __init__(self,commandProcces:Popen[bytes],commandLinkerObject:CommandLinkerObject) -> None:
        super().__init__(commandLinkerObject)
        self.commandProcces = commandProcces
        self.stdout = commandProcces.stdout
        self.stderr = commandProcces.stderr
    


    def kill(self) -> None:
        self.commandProcces.kill()

    """wait in a blocking way for the return code of the actor of this object"""
    async def wait(self,timeout:int) -> int:
        return self.commandProcces.wait(timeout)

    async def readOut(self, amount_of_bytes:int) -> bytes:
        if self.stdout is None:
            return b''
        return self.stdout.read(amount_of_bytes)
    
    async def readErr(self, amount_of_bytes:int) -> bytes:
        if self.stderr is None:
            return b''
        return self.stderr.read(amount_of_bytes)
    
    def getReaderFdOut(self):
        return self.stdout
    
    def getReaderFdErr(self):
        return self.stderr
    



    
class SSHCommandOutput(CommandOutput):
    """implementation of the interface using the SSHReader,
    this implementation is specificaly to interact with the asyncssh module
    see CommandOutput class for function documentation"""
    def __init__(self,commandProcces:SSHClientProcess[bytes],commandLinkerObject:CommandLinkerObject) -> None:
        super().__init__(commandLinkerObject)
        self.commandProcces = commandProcces
        self.stdout = commandProcces.stdout
        self.stderr = commandProcces.stderr

    
    def kill(self) -> None:
        self.commandProcces.kill()

    """wait in a blocking way for the return code of the actor of this object"""
    async def wait(self,timeout:int) -> int:
        finishedProcess = await self.commandProcces.wait(timeout=timeout)
        print("---------------------------------------------")
        if finishedProcess.returncode is None:
            raise RuntimeError("If the process is finished there should be a returncode -> report as bug")
        return finishedProcess.returncode

    async def readOut(self, amount_of_bytes:int) -> bytes:
        return await self.stdout.read(amount_of_bytes)
    
    async def readErr(self, amount_of_bytes:int) -> bytes:
        return await self.stderr.read(amount_of_bytes)
    
    def getReaderFdOut(self):
        return self.stdout
    
    def getReaderFdErr(self):
        return self.stderr
    

class CommandPassthrough(CommandOutput):
    """A way to create a fileStream that can be used as a CommandOutput by other functions"""
    def __init__(self,commandLinkerObject:CommandLinkerObject|None=None) -> None:
        super().__init__(commandLinkerObject)

        self.__readerOut, self.__writerOut = os.pipe()
        self.__outReadEmpty:bool = False
        self.__outWriteClosed:bool = False

        self.__readerErr, self.__writerErr = os.pipe()
        self.__errReadEmpty:bool = False
        self.__errWriteClosed:bool = False

        if commandLinkerObject is None:
            self.succeed(0)

        
    
    
    def kill(self) -> None:
        self.endWritingOut()
        self.endWritingErr()

    def succeed(self, retcode: int):
        self.endWritingErr()
        self.endWritingOut()
        super().succeed(retcode)

    def writeOut(self, bytes:bytes) -> None:
        if self.__outWriteClosed:
            raise(IOError("The FD for writing to Out has already been closed"))
        os.write(self.__writerOut,bytes)

    def endWritingOut(self) -> None:
        if not self.__outWriteClosed:
            self.__outWriteClosed = True
            os.close(self.__writerOut)
    
    async def readOut(self, amount_of_bytes:int) -> bytes:
        if self.__outReadEmpty:
            return b''
        
        if (data := os.read(self.__readerOut, amount_of_bytes)) == b'':
            self.__outReadEmpty =True
            os.close(self.__readerOut)
        return data
    
    def getReaderFdOut(self) -> int:
        return self.__readerOut
    
    def writeErr(self, bytes:bytes) -> None:
        if self.__outWriteClosed:
            raise(IOError("The FD for writing to Err has already been closed"))
        os.write(self.__writerErr,bytes)

    def endWritingErr(self) -> None:
        if not self.__errWriteClosed:
            self.__errWriteClosed = True
            os.close(self.__writerErr)

    async def readErr(self, amount_of_bytes:int) -> bytes:
        if self.__errReadEmpty:
            return b''
        
        if (data := os.read(self.__readerErr, amount_of_bytes)) == b'':
            self.__errReadEmpty =True
            os.close(self.__readerErr)
        
        return data
    
    def getReaderFdErr(self) -> int:
        return self.__readerErr
    


"""File notes

the read function needs verry thourough testing to make sure that all of the edge cases are the same
-> is it blocking when X bytes requested and there are not X bytes available
-> how does it react on reading X bytes when endof file has been reached
-> how does it react when the stream has been closed
=> these need to become documented so that further implementations can follow it

OutClosed has been removed due to there being no way to detect this withou blocking for the local intreface
-> detecting if there is stil data needs to be done manualy in the hooks
  -> if you recieve a b'' no further data will be readable 

  

CommandPassthrough can we fill the buffer and what happens if we do 
-> if hooks dont clear it fast enough what will happen
-> test this


"""