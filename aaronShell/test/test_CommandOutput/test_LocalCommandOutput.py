#!/usr/bin/env python3
# Copyright (C) 2023 Huawei Technologies Co., Ltd. All rights reserved.
# SPDX-License-Identifier: MIT
import unittest
from unittest import IsolatedAsyncioTestCase
import logging
import sys
import time
import asyncio
logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


from aaronShell.src.commandAST.command import command
from aaronShell.src.commandlineInterface.commandlineInterface import LocaleInterface, RemoteInterface


class TestCommandOutputLocal(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        asyncio.get_running_loop().slow_callback_duration = float('inf')

    async def testDataBlocks(self):
        async with (RemoteInterface('ftp.mynameisace.online',57429,username='yoyoyoyo') as remote,
                    LocaleInterface() as local):
            print("xxxx")
            commandOutput = await remote.run_command(command(r'"1\n2\n3";sleep 4;echo "4\n5\n6"'))
            #commandOutput = await remote.run_command(command(r"echo"),input=commandOutput1)
            print("aaaa")
            totalBytes = 0

            #the first echo returns 6 bytes we first read these out
            while (a := await commandOutput.readOut(10)):
                totalBytes += len(a)
                if totalBytes == 6:
                    break
            #start a timer
            t0 = time.time()
            (retCode,st) = await commandOutput.getOutPutAndReturnCode()

            #this command should block untill the sleep has finiched and there is new data to read
            t1 = time.time()
            print(t1 - t0)
            self.assertTrue(t1 - t0 > 3)
            print(f"retcode: {retCode}")
            print(f"retValue: {st}")





if __name__ == '__main__':
    unittest.main()