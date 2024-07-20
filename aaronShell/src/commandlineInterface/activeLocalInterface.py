from commandlineInterface import ActiveCommandlineInterface, CommandResult
from typing import Optional, Type
from types import TracebackType

from aaronShell.src.commandAST.Oldcommand import SingleCommand, Command, CompositeCommand

import subprocess
import sys

class TODO(Exception):
        def __init__(self, msg='This feature is not yet suported', *args, **kwargs): # type: ignore -> types dont matter for the exeptions
            super().__init__(msg, *args, **kwargs) # type: ignore -> types dont matter for the exeptions


class ActiveLocalInterface(ActiveCommandlineInterface):
    def close(self,exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        return False
    
    def location(self,
                 path):
        raise TODO()
    
    def stream(self,
                 path):
        raise TODO()

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
        raise TODO()
    
    

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
        def sucsess(value:int) -> bool:
            return value == 0
        

        (precomands, main_command, postcommands) = command.unwrap_command()
        if precomands is not None:
            for precommand in precomands:
                self.run_command_struct(precommand)


        with subprocess.Popen(
            main_command,
            shell=False,
            cwd=location,
            env=environment,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
        ) as shell_process:
            try:
                outs, errs = shell_process.communicate(input=std_input, timeout=timeout)
                retcode = shell_process.poll()
                output = outs
            except subprocess.TimeoutExpired as err:
                shell_process.kill()
                raise err
        
        #not a sucsessfull execution and not an alowed exit code
        #raise the appropriate error
        if not sucsess(retcode) and retcode not in ignore_ret_codes:
            raise subprocess.CalledProcessError(
                retcode,
                shell_process.args,
                )
        #not a sucsessfull execution but an alowed exit code
        #append the error to the output
        if not sucsess(retcode):
            output += shell_process.stderr.read()

        if postcommands is not None:
            for postcommand in postcommands:
                self.run_command_struct(postcommand)





        raise TODO()

    def copy_file(self,
                  location):
        raise TODO()
       
    def start_process(self,
                      command:Command,
                      input,
                      location,
                      envirenment,
                      timeout,
                      ignored_return_codes,
                      
                      #command logging arguments
                      print_command):
        raise TODO()