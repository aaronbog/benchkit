#!/usr/bin/env python3
# Copyright (C) 2023 Huawei Technologies Co., Ltd. All rights reserved.
# SPDX-License-Identifier: MIT
import unittest
import unittest.mock
import io
import benchkit.shell.shell as benchkitShell

class TestShellOut(unittest.TestCase):
    legalComands = [
        "./inputNeeded",
    ]

    privileged_Comands = [
        "ls noAccess",
    ]


    @classmethod
    def setUpClass(cls):
        benchkitShell.shell_out("sudo rm -rf noAccess")
        benchkitShell.shell_out("sudo mkdir noAccess")
        benchkitShell.shell_out("sudo chmod 700  noAccess")
    
    @classmethod
    def tearDownClass(cls):
        benchkitShell.shell_out("sudo rm -r noAccess")

    @staticmethod
    def _addPrivilege(command):
        return "sudo " + command

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_legal_comands(self,mock_stdout):
        f = open("demofile2.txt", "a")
        for command in self.legalComands:
            print(benchkitShell.shell_out(command))
            f.write(mock_stdout.getvalue())














if __name__ == '__main__':
    unittest.main()