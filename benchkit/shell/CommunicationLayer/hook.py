from abc import ABC, abstractmethod
import asyncio
from multiprocessing import Process
import os
from threading import Thread
from time import sleep
from typing import Any, Callable, Coroutine

from benchkit.shell.CommunicationLayer.comunication_handle import WritableOutput, Output

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
        process = Process(
                    target=self.hookFunction,
                    args=(
                        comandOutput,
                    ),
                )
        process.start()

    def getPassthrough(self):
        return self.__output

class ReaderHook(Hook):
    def pasAlongStdOut(self,comandOutput:Output,splitof:WritableOutput,output:WritableOutput):
        os.close(splitof.getReaderFdOut())
        os.close(output.getReaderFdOut())
        splitof = os.fdopen(splitof.getWriterFdOut(),mode="w")
        output = os.fdopen(output.getWriterFdOut(),mode="w")

        while True:
            data = comandOutput.readOut(1)
            if not data:
                break
            output.write(data.decode("utf-8"))
            if not self.__voidStdOut:
                splitof.write(data.decode("utf-8"))
        output.close()
        #if not already ended end the splitof datastream
        if not self.__voidStdOut:
            splitof.close()
        sleep(2)
        print("pasAlongStdOut stops")

    def pasAlongStdErr(self,comandOutput:Output,splitof:WritableOutput,output:WritableOutput):
        os.close(splitof.getReaderFdOut())
        os.close(output.getReaderFdOut())
        splitof = os.fdopen(splitof.getWriterFdErr(),mode="w")
        output = os.fdopen(output.getWriterFdErr(),mode="w")

        while True:
            data = comandOutput.readOut(1)
            if not data:
                break
            output.write(data.decode("utf-8"))
            if not self.__voidStdErr:
                splitof.write(data.decode("utf-8"))
        output.close()
        #if not already ended end the splitof datastream
        if not self.__voidStdErr:
            splitof.close()
        sleep(2)
        print("pasAlongStdErr stops")


    def __init__(self,hookFunction:Callable[[Output],None],voidStdOut=False,voidStdErr=False):
        self.__output = WritableOutput()
        self.__splitof = WritableOutput()

        self.__voidStdOut = voidStdOut
        if self.__voidStdOut:
            self.__splitof.endWritingOut()
        self.__voidStdErr = voidStdErr
        if self.__voidStdErr:
            self.__splitof.endWritingErr()
        self.hookFunction = hookFunction

    def startHookFunction(self,comandOutput:Output):
        process1 = Process(
                    target=self.pasAlongStdOut,
                    args=(
                        comandOutput,
                        self.__splitof,
                        self.__output
                    ),
                    daemon=True,
                )
        process2 = Process(
                    target=self.pasAlongStdErr,
                    args=(
                        comandOutput,
                        self.__splitof,
                        self.__output
                    ),
                    daemon=True,

                )
        process3 = Process(
                    target=self.hookFunction,
                    args=(
                        self.__splitof,
                    ),
                    daemon=True,
                )
        process1.start()
        process2.start()
        process3.start()
        self.__output.endWritingErr()
        self.__output.endWritingOut()
        process1.join()
        process2.join()
        process3.join()
        process1.close()
        process2.close()
        process3.close()
        print(f"a{self.__output.getWriterFdErr()}")
        # self.__output.endWritingErr()
        print(f"b{self.__output.getWriterFdOut()}")
        # self.__output.endWritingOut()



    def getPassthrough(self):
        return self.__output




# LLLLLLLLLLLLLLLLEEEEEEEEEEEEEEESSSSSSSSSSSSSSSSSSSS
# https://www.geeksforgeeks.org/python-os-pipe2-method/





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