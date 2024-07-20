from enum import Enum,auto

class Location:
    pass
class Generic:
    pass

class Node:
    pass

class CommandExecutableNode(Node):
    pass

class CommandExecutableStringNode(CommandExecutableNode):
    def __init__(self,arg:str) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class CommandExecutableGenericNode(CommandExecutableNode):
    def __init__(self,arg:Generic) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class CommandExecutableLocationNode(CommandExecutableNode):
    def __init__(self,arg:Location) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class ArgumentNode(Node):
    pass

class ArgumentStringNode(ArgumentNode):
    def __init__(self,arg:str) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class ArgumentUnsafeNode(ArgumentNode):
    def __init__(self,arg:str) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class ArgumentGenericNode(ArgumentNode):
    def __init__(self,arg:Generic) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class ArgumentLocationNode(ArgumentNode):
    def __init__(self,arg:Location) -> None:
        self.arg = arg
    def __str__(self):
        return f'{self.arg}'

class CommandNode(Node):
    pass

class ExecutableCommandNode(CommandNode):
    def __init__(self,executable:CommandExecutableNode,arguments:list[ArgumentNode]|None) -> None:
        self.executable=executable
        self.arguments=arguments
    def __str__(self):
            if self.arguments is None:
                return f'({self.executable})'  
            return f'({self.executable},{list(map(lambda obj: obj.__str__(), self.arguments))})'    

class ControlOperator(Enum):
    Pipe = auto(),
    AndThen = auto(),
    IfSucsess = auto(),
    IfFailed = auto(),
    def __str__(self):
        return f'<{self.name}>'

class ControlledCommandNode(CommandNode):
    def __init__(self,controlOperator:ControlOperator,commands:list[CommandNode]) -> None:
        self.controlOperator=controlOperator
        self.commands=commands
    def __str__(self):
            return f'({self.controlOperator},{list(map(lambda obj: obj.__str__(), self.commands))})'

class RedirectionError(Exception):
        """To conform to all platforms not all combinations of redirection are suported"""
        def __init__(self, msg='This type of redirection is not suported', *args, **kwargs): # type: ignore -> types dont matter for the exeptions
            super().__init__(msg, *args, **kwargs) # type: ignore -> types dont matter for the exeptions

class RedirectedCommandNode(CommandNode):
    def __init__(self,command:CommandNode) -> None:
        self.__stdIn:ArgumentNode|None = None
        self.__stdOut:ArgumentNode|None = None
        self.__stdErr:ArgumentNode|None = None
        self.stdOutIsAppend:bool = False

    def __setStdIn(self,redirectionArgument:ArgumentNode):
        if self.__stdIn is None:
            self.__stdIn = redirectionArgument
        else:
            raise RedirectionError('This command already has an inputstream: the original would be overwritten\n make a new node if this is intended')
            
    def __getStdIn(self):
        return self.__stdIn
    stdIn = property(__getStdIn, __setStdIn)

    def __setStdOut(self,redirectionArgument:ArgumentNode):
        if self.__stdOut is None:
            self.__stdOut = redirectionArgument
        else:
            raise RedirectionError('The output stream for this command is already redirected: incompatible for powershell')
            
    def __getStdOut(self):
        return self.__stdOut
    stdOut = property(__getStdOut, __setStdOut)

    def __setStdErr(self,redirectionArgument:ArgumentNode):
        if self.__stdErr is None:
            self.__stdErr = redirectionArgument
        else:
            raise RedirectionError('The Errput stream for this command is already redirected: incompatible for powershell')
            
    def __getStdErr(self):
        return self.__stdErr
    stdErr = property(__getStdErr, __setStdErr)