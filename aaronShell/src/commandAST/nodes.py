from abc import ABC
from typing import List, Self

from aaronShell.src.hooks.hooks import Hook

class Location:
    pass
class Generic:
    pass

class Node(ABC):
    pass
        

#abstract class for type hyrachy
class RunnableNode(Node):
    pass

class RunnableStringNode(RunnableNode):
    def __init__(self,command:str) -> None:
        self.command=command


#abstract class for type hyrachy
class ArgumentNode(Node):
    pass

class ArgumentStringNode(ArgumentNode):
    def __init__(self,argument:str) -> None:
        self.argument=argument

class ArgumentUnsafeNode(ArgumentNode):
    def __init__(self,argument:str) -> None:
        self.argument=argument

#abstract class for type hyrachy
class CommandNode(Node):
    def __init__(self) -> None:
        self.preRunHooks:List[Hook] = []
        self.postRunHooks:List[Hook] = []
    def addPreRunHook(self,hook:Hook) -> Self:
        self.preRunHooks.append(hook)
        return self
    def addPostRunHook(self,hook:Hook) -> Self:
        self.postRunHooks.append(hook)
        return self

class AtomicCommandNode(CommandNode):
    def __init__(self,command:RunnableNode,arguments:list[ArgumentNode]|None) -> None:
        super().__init__()
        self.command=command
        self.arguments=arguments

