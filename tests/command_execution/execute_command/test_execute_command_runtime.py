

import pathlib
from subprocess import TimeoutExpired
import threading
import time
import tracemalloc
import unittest

from benchkit.shell.command_execution.execute import execute_command
from tests.command_execution.execute_command.util import TestTimeout, eprint, generate_test_hook_lists, get_arguments_dict_list, print_open_fds, script_path_string, timeout

tracemalloc.start()

class RuntimeExecutionTests(unittest.TestCase):

    # @unittest.skip("disabled for debugging")
    def test_timeout(self) -> None:
        print_open_fds()
        """test to see if the command times out after the given time period"""

        # standard arguments
        arguments_list = get_arguments_dict_list(
            {
                'current_dir':[None, pathlib.Path(__file__).parent.resolve(),pathlib.Path('/')],
                'environment':[None,{'test':'test'},{'a':'12','b':'11'},{}],
                'timeout':[2],
                'ignore_ret_codes':[None,(1,),(1,7,),()],
            }
        )
        for arguments in arguments_list:
            # hook based argumens
            hooklist = generate_test_hook_lists()
            for input_hooks,output_hooks,_ in hooklist:
                try:
                # execution
                    with timeout(20):
                        with self.assertRaises(TimeoutExpired):
                            p = execute_command(
                                    [script_path_string("runForever")],
                                    ordered_output_hooks=output_hooks,
                                    ordered_input_hooks=input_hooks,
                                    **arguments,
                                )

                            # result gathering
                            p.get_return_code()

                except TestTimeout:
                    self.fail(
                        "execution timed out, but not by the timeout argument"
                    )
        print_open_fds()

    # @unittest.skip("disabled for debugging")
    def test_fill_std_err(self) -> None:
        print_open_fds()
        """test to see if the command times out after the given time period"""

        # standard arguments
        arguments_list = get_arguments_dict_list(
            {
                'current_dir':[None, pathlib.Path(__file__).parent.resolve(),pathlib.Path('/')],
                'environment':[None,{'test':'test'},{'a':'12','b':'11'},{}],
                'timeout':[None,20,99999999999],
                'ignore_ret_codes':[None,(1,),(1,7,),()],
            }
        )
        for arguments in arguments_list:
            t = time.time()
            # hook based argumens
            hooklist = generate_test_hook_lists()
            for input_hooks,output_hooks,_ in hooklist:
                eprint(arguments)
                try:
                # execution
                    with timeout(22):
                        p = execute_command(
                                [script_path_string("fillOutThenErr")],
                                ordered_output_hooks=output_hooks,
                                ordered_input_hooks=input_hooks,
                                **arguments,
                            )

                        # result gathering
                        p.get_return_code()
                except TestTimeout:
                    self.fail(
                        "execution timed out"
                    )
            eprint(time.time() - t)
        print_open_fds()

    # @unittest.skip("disabled for debugging")
    def test_fill_std_out(self) -> None:
        """test to see if the command times out after the given time period"""
        print_open_fds()
        # standard arguments
        arguments_list = get_arguments_dict_list(
            {
                'current_dir':[None, pathlib.Path(__file__).parent.resolve(),pathlib.Path('/')],
                'environment':[None,{'test':'test'},{'a':'12','b':'11'},{}],
                'timeout':[None,20,99999999999],
                'ignore_ret_codes':[None,(1,),(1,7,),()],
            }
        )
        for arguments in arguments_list:
            eprint(arguments)
            for thread in threading.enumerate():
                eprint(f"    {thread.name}")
            # hook based argumens
            hooklist = generate_test_hook_lists()
            for input_hooks,output_hooks,_ in hooklist:
                try:
                # execution
                    with timeout(22):
                        p = execute_command(
                                [script_path_string("fillErrThenOut")],
                                ordered_output_hooks=output_hooks,
                                ordered_input_hooks=input_hooks,
                                **arguments,
                            )

                        # result gathering
                        p.get_return_code()

                except TestTimeout:
                    self.fail(
                        "execution timed out"
                    )
            print_open_fds()
        print_open_fds()
