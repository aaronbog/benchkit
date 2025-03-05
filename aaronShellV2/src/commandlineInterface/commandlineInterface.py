from abc import ABC, abstractmethod
import asyncio
import subprocess
from threading import Thread
import asyncssh
from asyncssh import SSHClientConnection
from aaronShell.src.commandAST.nodes import *
from aaronShell.src.commandlineInterface.dataStructs import *

from typing import List, Optional, Type
from types import TracebackType

from aaronShell.src.commandlineInterface.dataStructs import CommandOutput, LocalCommandOutput, CommandPassthrough
from aaronShell.src.hooks.hooks import Hook

class ActiveCommandlineInterface(ABC):

    def _resolveHooks(self,commandOutput:CommandOutput,hooks:List[Hook]) -> CommandOutput:
        lastOut = commandOutput
        for hook in hooks:
            hook.startHookFunction(lastOut)
            lastOut = hook.getPassthrough()
        return lastOut
    
    async def _timout_and_retcode_update(self,commandOutput:LocalCommandOutput,timeout:int):
        try:
            retcode = await commandOutput.wait(timeout)
            commandOutput.succeed(retcode)
        except Exception as e:
            commandOutput.fatalError(1,e)

    """close is never called by the enduser of the interface, this is needed for the __exit__ call"""
    @abstractmethod
    async def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        pass
    
    @abstractmethod
    async def run_command(self,
                    command:CommandNode,
                    input:CommandOutput = CommandPassthrough(),
                    ) -> CommandOutput:
        pass
    

class ActiveRemoteInterface(ActiveCommandlineInterface):
    def __init__(self,connection:SSHClientConnection) -> None:
        self.connection:SSHClientConnection = connection

    async def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        await self.connection.__aexit__(exc_type,exc_value,traceback)
        return False
    
    def __atomicCommandToString(self,atomicCommand:AtomicCommandNode) -> str:
        arguments_as_string = ""
        if atomicCommand.arguments is not None:
            arguments_as_string:str = " ".join(map(self.__argumentNodeToString,atomicCommand.arguments))
        return self.__runnableNodeToString(atomicCommand.command) + " " + arguments_as_string

    def __runnableNodeToString(self,RunnableNode:RunnableNode) -> str:
        if type(RunnableNode) is RunnableStringNode:
            return RunnableNode.command
        raise TypeError("there are no other Runnable that chould get to the execution step")

    def __argumentNodeToString(self,argumentNode:ArgumentNode) -> str:
        if type(argumentNode) is ArgumentStringNode:
            return argumentNode.argument
        if type(argumentNode) is ArgumentUnsafeNode:
            return argumentNode.argument
        raise TypeError("there are no other argument that chould get to the execution step")

    async def run_command(self,
                    command:CommandNode,
                    input:CommandOutput = CommandPassthrough(),
                    ) -> CommandOutput:
        if type(command) is AtomicCommandNode:
            #apply all of the prerun hooks
            hookedInput = self._resolveHooks(input,command.preRunHooks)
            
            #get the equivelant string for the command node
            commandString = self.__atomicCommandToString(command)


            procedure = await self.connection.create_process(commandString,
                                                             stdin=hookedInput.getReaderFdOut(),
                                                             stdout=subprocess.PIPE,
                                                             stderr=subprocess.PIPE)
            
            output = SSHCommandOutput(procedure,hookedInput.commandLinkerObject)

            #we need to be able to monitor the command and signal if it errors and or finishes
            thread1 = Thread(target = lambda x,y: asyncio.run(self._timout_and_retcode_update(x,y)), args = (output,6))
            thread1.start()

            #apply all of the postrun hooks
            hookedInput = self._resolveHooks(output,command.postRunHooks)

            #return the universal structure
            return hookedInput



        
        raise TypeError("there are no other command types that chould get to the execution step")

class ActiveLocalInterface(ActiveCommandlineInterface):
    async def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        return False
    
    def __atomicCommandToString(self,atomicCommand:AtomicCommandNode) -> str:
        arguments_as_string = ""
        if atomicCommand.arguments is not None:
            arguments_as_string:str = " ".join(map(self.__argumentNodeToString,atomicCommand.arguments))
        return self.__runnableNodeToString(atomicCommand.command) + " " + arguments_as_string
    
    def __runnableNodeToString(self,RunnableNode:RunnableNode) -> str:
        if type(RunnableNode) is RunnableStringNode:
            return RunnableNode.command
        raise TypeError("there are no other Runnable that chould get to the execution step")

    def __argumentNodeToString(self,argumentNode:ArgumentNode) -> str:
        if type(argumentNode) is ArgumentStringNode:
            return argumentNode.argument
        if type(argumentNode) is ArgumentUnsafeNode:
            return argumentNode.argument
        raise TypeError("there are no other argument that chould get to the execution step")
            
 
        

        

    async def run_command(self,
                    #command functionality arguments
                    command:CommandNode,
                    input:CommandOutput = CommandPassthrough(),
                    ) -> CommandOutput:
        
        if type(command) is AtomicCommandNode:
            #apply all of the prerun hooks
            hookedInput = self._resolveHooks(input,command.preRunHooks)
            
            #get the equivelant string for the command node
            commandString = self.__atomicCommandToString(command)

            #running the actual command
            procedure = subprocess.Popen(commandString, shell=True,
                                         stdin=hookedInput.getReaderFdOut(),
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         start_new_session = True)
            
            #converting the output to a universal structure
            output = LocalCommandOutput(procedure,hookedInput.commandLinkerObject)

            #TODO: the timeout is hardcoded here to 6 seconds this NEEDS to be changable by the end user
            # this probably needs to become a ast node atribute for attomic commands
            # problem -> we cant set timeouts on entire command structures in total only on the parts of it
            # i dont know if this is a problem but for now i will not see it as such


            #we need to be able to monitor the command and signal if it errors and or finishes
            thread1 = Thread(target = lambda x,y: asyncio.run(self._timout_and_retcode_update(x,y)), args = (output,6))
            thread1.start()

            #apply all of the postrun hooks
            hookedInput = self._resolveHooks(output,command.postRunHooks)

            #return the universal structure
            return hookedInput
        
        raise TypeError("there are no other command types that chould get to the execution step")

        


class CommandlineInterface(ABC):

    def __init__(self):
        self.managedInstance=None
        self.managedInstanceCount=0
    
    # this is a wrapped function and should not be overwritten
    # _enter implements the actual logic for subclassing
    async def __aenter__(self) -> ActiveCommandlineInterface:
        self.managedInstance = await self.create()
        self.managedInstanceCount += 1
        return self.managedInstance
    
    @abstractmethod
    async def create(self) -> ActiveCommandlineInterface:
        pass
    
    # this is a wrapped function and should not be overwritten
    # close implements the actual logic for subclassing
    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        self.managedInstanceCount -= 1
        if self.managedInstanceCount == 0:
            retval:bool = await self.managedInstance.close(exc_type, exc_value, traceback) # type: ignore managedInstanceCount makes sure the type is correct
            self.managedInstance = None
            return retval
        return False
    

class RemoteInterface(CommandlineInterface):
    def __init__(self,hostname:str,port:int,username:str):
        self.hostname = hostname
        self.port     = port
        self.username = username 
        super().__init__()

    async def create(self) -> ActiveRemoteInterface:
        connection:SSHClientConnection = await asyncssh.connect(self.hostname,self.port,username=self.username,encoding =None)
        return ActiveRemoteInterface(connection)
    

class LocaleInterface(CommandlineInterface):
    def __init__(self):
        super().__init__()

    async def create(self) -> ActiveLocalInterface:
        return ActiveLocalInterface()