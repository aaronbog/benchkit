from abc import ABC, abstractmethod
import asyncio
from threading import Thread
from typing import Any, Callable, Coroutine

from aaronShell.src.commandlineInterface.dataStructs import CommandOutput, CommandPassthrough

class Hook(ABC):
    @abstractmethod
    def startHookFunction(self,comandOutput:CommandOutput) -> None:
        pass

    @abstractmethod
    def getPassthrough(self) -> CommandPassthrough:
        pass


class WriterHook(Hook):
    def __init__(self,hookFunction:Callable[[CommandOutput,CommandPassthrough],Coroutine[Any, Any, None]]):
        self.__output = CommandPassthrough()
        self.hookFunction = hookFunction

    def wrapHookfunction(self,comandOutput:CommandOutput):
        asyncio.run(self.hookFunction(comandOutput,self.__output))
    
    def startHookFunction(self,comandOutput:CommandOutput):
        thread = Thread(target = lambda inp,out: asyncio.run(self.hookFunction(inp,out)), args = (comandOutput,self.__output))
        thread.start()

    def getPassthrough(self):
        return self.__output
    
class ReaderHook(Hook):
    async def pasAlongStdOut(self,comandOutput:CommandOutput):
        while True:
            data = await comandOutput.readOut(1)
            if not data:
                break
            self.__output.writeOut(data)
            if not self.__voidStdOut:
                self.__splitof.writeOut(data)
        self.__output.endWritingOut()
        #if not already ended end the splitof datastream
        if not self.__voidStdOut:
            self.__splitof.endWritingOut()
        
    async def pasAlongStdErr(self,comandOutput:CommandOutput):
        while True:
            data = await comandOutput.readErr(1)
            if not data:
                break
            self.__output.writeErr(data)
            if not self.__voidStdErr:
                self.__splitof.writeErr(data)
        self.__output.endWritingErr()
         #if not already ended end the splitof datastream
        if not self.__voidStdErr:
            self.__splitof.endWritingErr()

    def __init__(self,hookFunction:Callable[[CommandOutput],Coroutine[Any, Any, None]],voidStdOut=False,voidStdErr=False):
        self.__output = CommandPassthrough()
        self.__splitof = CommandPassthrough()

        self.__voidStdOut = voidStdOut
        if self.__voidStdOut:
            self.__splitof.endWritingOut()
        self.__voidStdErr = voidStdErr
        if self.__voidStdErr:
            self.__splitof.endWritingErr()
        self.hookFunction = hookFunction

    def startHookFunction(self,comandOutput:CommandOutput):
        thread1 = Thread(target = lambda x: asyncio.run(self.pasAlongStdOut(x)), args = (comandOutput,))
        thread2 = Thread(target = lambda x: asyncio.run(self.pasAlongStdErr(x)), args = (comandOutput,))
        thread3 = Thread(target = lambda x: asyncio.run(self.hookFunction(x)), args = (self.__splitof,))
        thread1.start()
        thread2.start()
        thread3.start()

    def getPassthrough(self):
        return self.__output
    

"""
file notes
voiding something for the reader function can be done in a more efficient method,
we could create an empty passthrouh for the splitof part and just replace the stdOut in the __output
would need to check if this is a clean solution or more of a hack
the current implementation is consisten and 'clean' albe it with a lot of overhead


TODO implement the voiding of certain streams for the writer hooks
this makes it less likely people will make mistakes by ignoring streams and blocking

TODO implement passtrough of certian streams for writer hooks
this makes it less likely people will make mistakes by ignoring streams and blocking

"""
        
        