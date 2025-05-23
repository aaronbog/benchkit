from abc import ABC, abstractmethod
import asyncio
from multiprocessing import Process
from threading import Thread
from typing import Any, Callable, Coroutine
from benchkit.shell.CommunicationLayer.comunication_handle import Output, WritableOutput

class Hook(ABC):
    @abstractmethod
    def startHookFunction(self,comandOutput:Output) -> None:
        pass

    @abstractmethod
    def getPassthrough(self) -> WritableOutput:
        pass


class WriterHook(Hook):
    def __init__(self,hookFunction:Callable[[Output,WritableOutput],None]):
        self.__output = WritableOutput()
        self.hookFunction = hookFunction

    def startHookFunction(self,comandOutput:Output):
        p = Process(
            target=self.hookFunction,
            args=(
                comandOutput,
                self.__output
            )
        )
        p.start()
        self.__output.endWritingErr()
        self.__output.endWritingOut()

    def getPassthrough(self):
        return self.__output



class ReaderHook(Hook):

    @staticmethod
    def pasAlongStdOut(input:Output ,output:WritableOutput,splitof:WritableOutput,void_stdout:bool):
        while True:
            data = input.readOut(1)
            if not data:
                break
            output.writeOut(data)
            # if not void_stdout:
            splitof.writeOut(data)
        # output.endWritingOut()
        #if not already ended end the splitof datastream
        if not void_stdout:
            print("?????")
            # splitof.endWritingOut()

        output.endWritingErr()
        output.endWritingOut()
        splitof.endWritingErr()
        splitof.endWritingOut()

    @staticmethod
    def pasAlongStdErr(input:Output ,output:WritableOutput,splitof:WritableOutput,void_stderr:bool):
        while True:
            data = input.readErr(1)
            if not data:
                break
            output.writeErr(data)
            # if not void_stderr:
            splitof.writeErr(data)
        # output.endWritingErr()
        #if not already ended end the splitof datastream
        if not void_stderr:
            print("?????")
            # splitof.endWritingErr()

        output.endWritingErr()
        output.endWritingOut()
        splitof.endWritingErr()
        splitof.endWritingOut()

    def __init__(self,hookFunction:Callable[[Output],None],voidStdOut=False,voidStdErr=False):
        self.__output = WritableOutput()
        self.__splitof = WritableOutput()
        self.__voidStdErr = voidStdErr
        self.__voidStdOut = voidStdOut


    def startHookFunction(self,comandOutput:Output):
        p1 = Process(
            target=self.pasAlongStdOut,
            args=(
                comandOutput,
                self.__output,
                self.__splitof,
                self.__voidStdOut
            )
        )
        p2 = Process(
            target=self.pasAlongStdErr,
            args=(
                comandOutput,
                self.__output,
                self.__splitof,
                self.__voidStdErr
            )
        )
        # p3 = Process(
        #     target=self.hookFunction,
        #     args=(
        #         self.__splitof,
        #     )
        # )
        p1.start()
        p2.start()
        # p3.start()
        self.__output.endWritingErr()
        self.__output.endWritingOut()
        self.__splitof.endWritingErr()
        self.__splitof.endWritingOut()




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
