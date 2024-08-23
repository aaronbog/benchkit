from abc import ABC, abstractmethod
import subprocess

from asyncssh import SSHClientConnection
from aaronShell.src.commandAST.nodes import *
from aaronShell.src.commandlineInterface.dataStructs import *

from typing import List, Optional, Type
from types import TracebackType

from aaronShell.src.commandlineInterface.dataStructs import CommandOutput, LocalCommandOutput, CommandPassthrough
from aaronShell.src.hooks.hooks import Hook

class ActiveCommandlineInterface(ABC):
    """close is never called by the enduser of the interface, this is needed for the __exit__ call"""
    @abstractmethod
    async def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        pass
    
    @abstractmethod
    async def run_command(self,
                    command:CommandNode,
                    input:CommandOutput = CommandPassthrough(createEmpty = True),
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
                    input:CommandOutput = CommandPassthrough(createEmpty = True),
                    ) -> CommandOutput:
        if type(command) is AtomicCommandNode:
            commandString = self.__atomicCommandToString(command)
            procedure = await self.connection.create_process(commandString, stdin=input.getReaderFdOut(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return SSHCommandOutput(procedure.stdout,procedure.stderr)
        
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

    def resolveHooks(self,commandOutput:CommandOutput,hooks:List[Hook]) -> CommandOutput:
        lastOut = commandOutput
        for hook in hooks:
            hook.startHookFunction(lastOut)
            lastOut = hook.getPassthrough()
        return lastOut

    async def run_command(self,
                    #command functionality arguments
                    command:CommandNode,
                    input:CommandOutput = CommandPassthrough(createEmpty = True),
                    ) -> CommandOutput:
        if type(command) is AtomicCommandNode:
            commandString = self.__atomicCommandToString(command)
            hookedInput = self.resolveHooks(input,command.preRunHooks)
            procedure = subprocess.Popen(commandString, shell=True,
                                         stdin=hookedInput.getReaderFdOut(),
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            output = LocalCommandOutput(procedure.stdout,procedure.stderr)
            hookedInput = self.resolveHooks(output,command.postRunHooks)
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
    # _exit implements the actual logic for subclassing
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
        connection = await asyncssh.connect(self.hostname,self.port,username=self.username,encoding =None)
        return ActiveRemoteInterface(connection)
    

class LocaleInterface(CommandlineInterface):
    def __init__(self):
        super().__init__()

    async def create(self) -> ActiveLocalInterface:
        return ActiveLocalInterface()