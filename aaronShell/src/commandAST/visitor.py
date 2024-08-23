#!/usr/bin/env python3
from aaronShell.src.commandAST.command import command
from aaronShell.src.commandAST.nodes import *


class Visitor(ABC):
    def visitArgumentStringNode(self,node:ArgumentStringNode) -> Node:
        return node
    def visitArgumentUnsafeNode(self,node:ArgumentUnsafeNode) -> Node:
        return node
    def visitAtomicCommandNode(self,node:AtomicCommandNode) -> Node:
        node.command = self.visit(node.command)
        if node.arguments is not None:
            node.arguments = list(map(self.visit, node.arguments))
        return node
    def visitRunnableStringNode(self,node:RunnableStringNode) -> Node:
        return node
    
    

    def visit[T:Node](self,node:T) -> T: 
        return eval("self.visit" + type(node).__name__ + "(node)")

class printAST(Visitor):
    #
    def __init__(self) -> None:
        self.indent = -1
    def printWithIndent(self,content:str):
        print("|"*self.indent + content)
    def printType(self,node:Node):
        self.printWithIndent(type(node).__name__)


    def visitArgumentStringNode(self,node:ArgumentStringNode) -> Node:
        self.printWithIndent(node.argument)
        return super().visitArgumentStringNode(node)
    def visitArgumentUnsafeNode(self,node:ArgumentUnsafeNode) -> Node:
        self.printWithIndent(node.argument)
        return super().visitArgumentUnsafeNode(node)
    def visitAtomicCommandNode(self,node:AtomicCommandNode) -> Node:
        return super().visitAtomicCommandNode(node)
    def visitRunnableStringNode(self,node:RunnableStringNode) -> Node:
        self.printWithIndent(node.command)
        return super().visitRunnableStringNode(node)
    
    

    def visit[T:Node](self,node:T) -> T:
        self.indent += 1
        self.printType(node)
        self.indent += 1
        ret = super().visit(node)
        self.indent -= 2
        return ret

def localtests():
    v = printAST()
    v.visit(command("'ls -R'",["arg0","arg1"]))

if __name__ == "__main__":
    localtests()