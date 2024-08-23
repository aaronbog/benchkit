from abc import ABC,abstractmethod
from io import BufferedReader

import os
import asyncssh

class CommandOutput(ABC):
    """interface to communicate with command output on all platforms, functions are async due to compatibility"""    
    @abstractmethod
    async def readOut(self, amount_of_bytes:int) -> bytes:
        """reads at most amount_of_bytes from the available stdout"""
        pass
    
    @abstractmethod
    async def readErr(self, amount_of_bytes:int) -> bytes:
        """reads at most amount_of_bytes from the available stderr"""
        pass
    
    @abstractmethod
    def getReaderFdOut(self):
        pass
    
    @abstractmethod
    def getReaderFdErr(self):
        pass

class LocalCommandOutput(CommandOutput):
    """implementation of the interface using standard IO interactions,
    this implementation is specificaly to interact with the subprocesses module
    see CommandOutput class for function documentation"""
    def __init__(self,stdout:BufferedReader|None,stderr:BufferedReader|None) -> None:
        self.stdout = stdout
        self.stderr = stderr
    
    async def readOut(self, amount_of_bytes:int) -> bytes:
        if self.stdout is None:
            return b''
        return self.stdout.read1(amount_of_bytes)
    
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
    def __init__(self,stdout:asyncssh.SSHReader[bytes],stderr:asyncssh.SSHReader[bytes]) -> None:
        self.stdout = stdout
        self.stderr = stderr
    
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
    def __init__(self,createEmpty:bool = False) -> None:
        self.readerOut, self.writerOut = os.pipe()
        self.readerErr, self.writerErr = os.pipe()
        if createEmpty:
            self.endWritingOut()
            self.endWritingErr()

    def writeOut(self, bytes:bytes) -> None:
        os.write(self.writerOut,bytes)

    def endWritingOut(self) -> None:
        os.close(self.writerOut)
    
    async def readOut(self, amount_of_bytes:int) -> bytes:
        return os.read(self.readerOut, amount_of_bytes)
    
    def getReaderFdOut(self) -> int:
        return self.readerOut
    
    def writeErr(self, bytes:bytes) -> None:
        os.write(self.writerErr,bytes)

    def endWritingErr(self) -> None:
        os.close(self.writerErr)

    async def readErr(self, amount_of_bytes:int) -> bytes:
        return os.read(self.readerErr, amount_of_bytes)
    
    def getReaderFdErr(self) -> int:
        return self.readerErr
    


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