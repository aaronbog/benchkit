#!/usr/bin/env python3

from aaronShell.src.commandAST.nodes import *
    
class CommandArgumentRawUnsafe:
    def __init__(self,argument:str) -> None:
        self.argument = argument

class Command:
    def __str__(self):
            return f'({self.ast})'  
    def __process_program(self,program:str|Generic|Location) -> CommandExecutableNode:
        if type(program) is str:
            return CommandExecutableStringNode(program)
        elif type(program) is Generic:
            return CommandExecutableGenericNode(program)
        elif type(program) is Location:
            return CommandExecutableLocationNode(program)
        else:
            raise TypeError()
    def __process_argument(self,program:str|Generic|Location|CommandArgumentRawUnsafe) -> ArgumentNode:    
        if type(program) is str:
            return ArgumentStringNode(program)
        elif type(program) is Generic:
            return ArgumentGenericNode(program)
        elif type(program) is Location:
            return ArgumentLocationNode(program)
        elif type(program) is CommandArgumentRawUnsafe:
            return ArgumentUnsafeNode(program.argument)
        else:
            raise TypeError()

    def __init__(self, program:str|Generic|Location, arguments:list[str|Generic|Location|CommandArgumentRawUnsafe]|None = None) -> None:
        if type(program) is str:
            #program could be a full command, strip of the actual command from its arguments first
            if program.startswith("'"):
                index = program.find("'",1)
                new_program = program[0:index+1]
                extra_arguments = program[index+1:-1].strip()
                program = new_program
                if arguments is None:
                    arguments = [extra_arguments]
                else:
                    arguments = [extra_arguments] + arguments
        if arguments is None:
            self.ast:CommandNode = ExecutableCommandNode(self.__process_program(program),
                                             None)
        else:
            self.ast:CommandNode = ExecutableCommandNode(self.__process_program(program),
                                            list(map(self.__process_argument,arguments)))

    def __simplifyControlledCommandNodes(self,ast:ControlledCommandNode):
        nodeOperator = ast.controlOperator
        new_command_list:list[CommandNode] = []
        for subcomand in ast.commands:
            if type(subcomand) is ControlledCommandNode and subcomand.controlOperator is nodeOperator:
                new_command_list.extend(subcomand.commands)
            else:
                new_command_list.append(subcomand)
        return ControlledCommandNode(nodeOperator,new_command_list)

    def pipe(self,command:'Command') -> 'Command':
        self.ast = self.__simplifyControlledCommandNodes(ControlledCommandNode(ControlOperator.Pipe,[self.ast,command.ast]))
        return self
    def andThen(self,command:'Command') -> 'Command':
        self.ast = self.__simplifyControlledCommandNodes(ControlledCommandNode(ControlOperator.AndThen,[self.ast,command.ast]))
        return self
    def ifSucsess(self,command:'Command') -> 'Command':
        self.ast = self.__simplifyControlledCommandNodes(ControlledCommandNode(ControlOperator.IfSucsess,[self.ast,command.ast]))
        return self
    def ifFailed(self,command:'Command') -> 'Command':
        self.ast = self.__simplifyControlledCommandNodes(ControlledCommandNode(ControlOperator.IfFailed,[self.ast,command.ast]))
        return self
    
    def stdIn(self,dest:str|Generic|Location|CommandArgumentRawUnsafe) -> 'Command':
        if not type(self.ast) is RedirectedCommandNode:
            self.ast = RedirectedCommandNode(self.ast)
        self.ast.stdIn = dest
        return self
    def stdOut(self,dest:str|Generic|Location|CommandArgumentRawUnsafe) -> 'Command':
        if not type(self.ast) is RedirectedCommandNode:
            self.ast = RedirectedCommandNode(self.ast)
        self.ast.stdIn = dest
        return self
    def stdErr(self,dest:str|Generic|Location|CommandArgumentRawUnsafe) -> 'Command':
        if not type(self.ast) is RedirectedCommandNode:
            self.ast = RedirectedCommandNode(self.ast)
        self.ast.stdErr = dest
        return self
    def stdOutAppend(self,dest:str|Generic|Location|CommandArgumentRawUnsafe) -> 'Command':
        if not type(self.ast) is RedirectedCommandNode:
            self.ast = RedirectedCommandNode(self.ast)
        self.ast.stdErr = dest
        self.ast.stdOutIsAppend = True
        return self