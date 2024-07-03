#!/usr/bin/env python3

import shlex
from abc import ABC, abstractmethod

# class envVar:
#     def __init__(self, program, arguments):

class Command:
    @abstractmethod
    def get_command(self) -> str:
        pass
    
    def pipe(self, command) -> 'CompositeCommand':
        return CompositeCommand(self.get_command() + " | " + command.get_command()) 

class SingleCommand(Command):
    def __init__(self, program, arguments):
        #here we can introduce the concept of platform specific program names
        self.program = program
        #here we can introduce arguments that are not standard such as locations
        self.arguments = arguments

    def get_command(self) -> str:
        " ".join([self.program] + self.arguments)
        return shlex.join(shlex.split(" ".join([self.program] + self.arguments)))

#usefull for type matching since the internals of perf can not be a CompositeCommand
class CompositeCommand(Command):
    def __init__(self, command):
        #here we can introduce the concept of platform specific program names
        self.command = command

    def get_command(self) -> str:
        return self.command