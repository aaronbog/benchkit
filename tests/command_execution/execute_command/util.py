# Copyright (C) 2025 Vrije Universiteit Brussel. All rights reserved.
# SPDX-License-Identifier: MIT

import itertools
import os
import pathlib
import signal
import threading
import sys
from time import sleep
from typing import Any, Dict, List, Optional, Tuple

from benchkit.shell.command_execution.io.stream import ReadableIOStream, WritableIOStream
from benchkit.shell.command_execution.io.hooks.basic_hooks import create_stream_line_logger_hook, create_voiding_result_hook, logger_line_hook, void_hook, void_input
from benchkit.shell.command_execution.io.hooks.hook import IOHook, IOResultHook, IOWriterHook, OutputHook


def eprint(s:Any) -> None:
    print(s,file=sys.stderr)

def get_fds_count() -> int:
    fds = os.listdir('/proc/self/fd/')
    return len(fds)

def print_open_fds(to_err:bool=True) -> None:
    string = f'amount of open file descriptors: {get_fds_count()}'
    if to_err:
        eprint(string)
    else:
        print(string)


class TestTimeout(Exception):
    pass


class timeout:
    def __init__(self, seconds:int, error_message:Optional[str]=None):
        if error_message is None:
            error_message = "test timed out after {}s.".format(seconds)
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TestTimeout(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)

class FdLeak(Exception):
    pass

class fd_checker:
    def __init__(self,tolerance:int=6) -> None:
        self.tolerance = tolerance
        self.fd_count:int = 0

    def __enter__(self):
        self.fd_count = get_fds_count()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            return
        if abs(self.fd_count - get_fds_count()) > self.tolerance:
            raise FdLeak("This with statement ended up with more file descriptorst than when it started")

class ThreadLeak(Exception):
    pass

class thread_checker:
    def __init__(self,tolerance:int=6) -> None:
        self.tolerance = tolerance
        self.thread_count:int = 0

    def __enter__(self):
        self.thread_count = threading.active_count()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            return
        if abs(self.thread_count - threading.active_count()) > self.tolerance:
            raise ThreadLeak("This with statement ended up with more threads than when it started")

def script_path_string(script_name: str):
    folder = pathlib.Path(__file__).parent.resolve()
    print(folder)
    return str(folder / f"./shell_scripts/{script_name}.sh")

def get_arguments_dict_list(
    overwrite_arguments_dict: Dict[str, Any] | None = None,
):
    if overwrite_arguments_dict is None:
        overwrite_arguments_dict = {}

    arguments_dict:Dict[str,Any] = {}

    for argument_key in overwrite_arguments_dict:
        arguments_dict[argument_key] = overwrite_arguments_dict[argument_key]

    keys:List[str] = []
    arguments:List[Any] = []

    for key, arugments in arguments_dict.items():
        keys.append(key)
        arguments += [arugments]
    argument_permutations = itertools.product(*arguments)
    result_list:List[Dict[str,Any]] = []
    for argument_permutation in list(argument_permutations):
        result_list.append(dict(zip(keys, argument_permutation)))
    return result_list

def generate_test_hook_lists(force_output:bool=False,dont_void_output:bool=False) -> List[Tuple[List[IOHook],List[OutputHook],Optional[IOResultHook]]]:

    def useless_func(input_object: ReadableIOStream, output_object: WritableIOStream):
        outline = input_object.read(10)
        while outline:
            output_object.write(outline)
            outline = input_object.read(10)

    def gen_useless_input():
        return IOWriterHook(useless_func)

    def gen_logging_input():
        return create_stream_line_logger_hook("log_input" + " {}")

    def gen_useless_output():
        return OutputHook(IOWriterHook(useless_func),IOWriterHook(useless_func))

    def gen_logging_output():
        return logger_line_hook(
            "\033[34m[OUT | ]\033[0m" + " {}",
            "\033[91m[ERR | ]\033[0m" + " {}",
        )

    def gen_result_output():
        output_hook_object = create_voiding_result_hook()
        voiding_result_hook = OutputHook(output_hook_object,IOWriterHook(void_input))
        return voiding_result_hook, output_hook_object

    hooklist:List[Tuple[List[IOHook],List[OutputHook],Optional[IOResultHook]]] = []

    for option in itertools.product([True,False],[True,False],[True,False],[True,False],[True,False]):
        output_hooks:List[OutputHook] = []
        input_hooks:List[IOHook] = []
        output_object = None
        if option[0]:
            input_hooks.append(gen_useless_input())
        if option[1]:
            input_hooks.append(gen_logging_input())
        if option[2]:
            output_hooks.append(gen_useless_output())
        if option[3]:
            output_hooks.append(gen_logging_output())
        if option[4] or force_output:
            hook, obj = gen_result_output()
            output_object = obj
            output_hooks.append(hook)
        if not dont_void_output:
            output_hooks.append(void_hook())

        hooklist.append((input_hooks, output_hooks, output_object))
    return hooklist