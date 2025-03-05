#!/usr/bin/env python3

from aaronShell.src.commandAST.nodes import *
    
class CommandArgumentRawUnsafe:
    def __init__(self,argument:str) -> None:
        self.argument = argument

def process_program(program:str|Generic|Location) -> RunnableNode:
    if type(program) is str:
        return RunnableStringNode(program)
    else:
        raise TypeError()
def process_argument(argument:str|Generic|Location|CommandArgumentRawUnsafe) -> ArgumentNode:    
    if type(argument) is str:
        return ArgumentStringNode(argument)
    elif type(argument) is CommandArgumentRawUnsafe:
        return ArgumentUnsafeNode(argument.argument)
    else:
        raise TypeError()

def command(program:str|Generic|Location, arguments:list[str|Generic|Location|CommandArgumentRawUnsafe]|None = None) -> CommandNode:
    if type(program) is str:
            #program could be a full command, strip of the actual command from its arguments first
            program = program.strip()
            if program.startswith("'"):
                index = program.find("'",1)
            elif program.startswith('"'):
                index = program.find('"',1)
            else:
                index = program.find(" ",1)
            new_program = program[0:index+1]
            extra_arguments = program[index+1:].strip()
            program = new_program
            if not extra_arguments:
                arguments = arguments
            elif arguments is None:
                arguments = [extra_arguments]
            else:
                arguments = [extra_arguments] + arguments
                
    if arguments is None:
        return AtomicCommandNode(process_program(program),
                                            None)
    else:
        return AtomicCommandNode(process_program(program),
                                    list(map(process_argument,arguments)))
    

def localtests():
    commandres = command("'ls -R'",["arg0","arg1"])
    print(commandres)
    commandres = command("'ls -R '",["arg0","arg1"])
    print(commandres)
    commandres = command("' ls -R'",["arg0","arg1"])
    print(commandres)
    commandres = command("ls -R",["arg0","arg1"])
    print(commandres)
    commandres = command("ls -R   ",["arg0","arg1"])
    print(commandres)
    commandres = command("   ls -R",["arg0","arg1"])
    print(commandres)
    commandres = command("ls     -R",["arg0","arg1"])
    print(commandres)

if __name__ == "__main__":
    localtests()