#!/usr/bin/env python3
# Copyright (C) 2023 Huawei Technologies Co., Ltd. All rights reserved.
# SPDX-License-Identifier: MIT
import unittest
import io
import logging
import sys
logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


from aaronShell.src.commandlineInterface.dataStructs import CommandPassthrough


class TestCommanndPassthrough(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.passthrough = CommandPassthrough()
        
    def tearDown(self):
        self.passthrough.endWritingOut()
        self.passthrough.endWritingErr()


    async def testDataTransferOut(self):
        self.passthrough.writeOut(b'ao')
        self.passthrough.endWritingErr()
        logger.info("await self.passthrough.readErr(20)")
        logger.info(await self.passthrough.readErr(1))
        logger.info(await self.passthrough.readErr(20))
        logger.info(await self.passthrough.readErr(20))
        logger.info(await self.passthrough.readErr(20))
    
    async def testDataTransferErr(self):
        self.passthrough.writeOut(b'ao')
        self.passthrough.endWritingErr()
        logger.info("await self.passthrough.readErr(20)")
        logger.info(await self.passthrough.readErr(1))
        logger.info(await self.passthrough.readErr(20))
        logger.info(await self.passthrough.readErr(20))
        logger.info(await self.passthrough.readErr(20))

if __name__ == '__main__':
    unittest.main()