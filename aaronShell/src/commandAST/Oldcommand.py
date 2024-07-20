#!/usr/bin/env python3

import shlex
from abc import ABC
from enum import Enum

class Operator(Enum):
    PIPE = 1,
    COMPOUND = 2
    

class Command(ABC):
    def pipe(self, command:'Command') -> 'CompositeCommand':
        return CompositeCommand(Operator.PIPE, [self, command])
    
    def Compound(self, command:'Command') -> 'CompositeCommand':
        return CompositeCommand(Operator.COMPOUND, [self, command])

    def prependGetPid(self) -> 'CompositeCommand':
        return CompositeCommand(Operator.COMPOUND, [SingleCommand("echo", ["$$"], raw=True), self])


class SingleCommand(Command):

    def __init__(self, program:str, arguments:list[str]|None = None,raw:bool=False):
        self.raw = raw
        if raw:
            cmd = program
            if arguments is not None:
                for a in arguments:
                    cmd += " " + a
            self.command_parts = [cmd]
        else:
            self.command_parts = shlex.split(program)
            if arguments is not None:
                for a in arguments:
                    self.command_parts += shlex.split(a)

    def unwrap_command(self) -> tuple[list[Command]|None,list[str],list[Command]|None]:
        return (None,self.command_parts,None)



    #TODO: this needs to be removed this is the responsibility of the comandline interface
    def get_command_string(self) -> str:
        if self.raw:
            return " ".join(self.command_parts)
        return shlex.join(self.command_parts)

#usefull for type matching since the internals of perf can not be a CompositeCommand
class CompositeCommand(Command):
    def __init__(self, opreator:Operator, commands:list[Command]):
        self.opreator = opreator
        self.commands = commands