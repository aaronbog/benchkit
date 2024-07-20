from aaronShell.src.commandAST.Oldcommand import Command, SingleCommand, CompositeCommand,Operator
from abc import ABC, abstractmethod
import paramiko

from typing import Optional, Type, Callable
from types import TracebackType


class CommandResult:
    def __init__(self,command:Command,exit_status:int,stdout:str,stderr:str) -> None:
        self.command     = command
        self.exit_status = exit_status
        self.stdout      = stdout
        self.stderr      = stderr

    def is_sucsess(self) -> bool:
        return self.exit_status == 0

class ActiveCommandlineInterface(ABC):
    """close is never called by the enduser of the interface, this is needed for the __exit__ call"""
    @abstractmethod
    def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        pass
    
    @abstractmethod
    def location(self,
                 path):
        pass
    
    @abstractmethod
    def stream(self,
                 path):
        pass

    @abstractmethod
    def run_command(self,
                    #command functionality arguments
                    command:Command,
                    input = None, #we want tis to be able to be a file, stream or string
                    location = None, #forcing this to be a location on the machine interface itself
                    environment = None, # wanted env vars
                    timeout = None, # timeout for the command
                    ignored_return_codes = None, # return codes that can be cleanly ignored and still give the result
                    
                    #command logging arguments
                    print_command = None
                    ) -> str:
        pass
    @abstractmethod
    def run_command_struct(self,
                    #command functionality arguments
                    command:Command,
                    input = None, #we want tis to be able to be a file, stream or string
                    location = None, #forcing this to be a location on the machine interface itself
                    environment = None, # wanted env vars
                    timeout = None, # timeout for the command
                    ignored_return_codes = None, # return codes that can be cleanly ignored and still give the result
                    
                    #command logging arguments
                    print_command = None
                    ) -> CommandResult:
        pass
    
    @abstractmethod
    def copy_file(self,
                  location):
        pass
    
    @abstractmethod    
    def start_process(self,
                      command:Command,
                      input,
                      location,
                      envirenment,
                      timeout,
                      ignored_return_codes,
                      
                      #command logging arguments
                      print_command):
        pass

class ActiveRemoteInterface(ActiveCommandlineInterface):
    def __init__(self,hostname:str,port:int,username:str):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.hostname = hostname
        self.port = port
        self.username = username
        self.client.connect(hostname=self.hostname,port=self.port,username=self.username)

    def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        self.client.close()
        return False

    @staticmethod
    def __get_comand(command:Command) -> str:
        if type(command) is SingleCommand:
            return ActiveRemoteInterface.__get_command_single(command)
        elif type(command) is CompositeCommand:
            return ActiveRemoteInterface.__get_command_composite(command)
        else:
            raise TypeError("can not get command from anything else than SingleCommand or CompositeCommand")
        

    @staticmethod
    def __get_command_single(command:SingleCommand) -> str:
        return command.get_command_string()
    
    @staticmethod
    def __get_command_composite(command:CompositeCommand) -> str:
        match command.opreator:
            case  Operator.PIPE:
                assert len(command.commands) == 2
                return ActiveRemoteInterface.__get_comand(command.commands[0]) + " | " + ActiveRemoteInterface.__get_comand(command.commands[1])
            case Operator.COMPOUND:
                ret = ActiveRemoteInterface.__get_comand(command.commands[0])
                for cmd in command.commands[1:]:
                    ret += ";" + ActiveRemoteInterface.__get_comand(cmd)
                return ret

    def run_command(self,command:Command) -> None:
        assert(isinstance(command, Command))

        stdin, stdout, stderr = self.client.exec_command(ActiveRemoteInterface.__get_comand(command))
        exit_status = stdout.channel.recv_exit_status()
        pid = int(stdout.readline())
        out=stdout.read()
        print(out)
        print(pid)
        print(exit_status)
    
class CommandlineInterface(ABC):

    def __init__(self,function:Callable[[],ActiveCommandlineInterface]):
        self.function=function
        self.managedInstance=None
        self.managedInstanceCount=0
    
    # this is a wrapped function and should not be overwritten
    # _enter implements the actual logic for subclassing
    def __enter__(self) -> ActiveCommandlineInterface:
        self.managedInstance = self.function()
        self.managedInstanceCount += 1
        return self.managedInstance
    
    # this is a wrapped function and should not be overwritten
    # _exit implements the actual logic for subclassing
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        self.managedInstanceCount -= 1
        if self.managedInstanceCount == 0:
            retval:bool = self.managedInstance.close(exc_type, exc_value, traceback) # type: ignore managedInstanceCount makes sure the type is correct
            self.managedInstance = None
            return retval
        return False
    
    @classmethod
    def remoteInterface(cls,hostname:str,port:int,username:str):
        CommandlineInterface(lambda:ActiveRemoteInterface(hostname,port,username))

    @classmethod
    def localInterface(cls):
        CommandlineInterface(lambda:ActiveLocalInterface())