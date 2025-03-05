#!/usr/bin/env python3
# Copyright (C) 2023 Huawei Technologies Co., Ltd. All rights reserved.
# SPDX-License-Identifier: MIT
import unittest
import io


class TestCommanndPassthroughG(unittest.TestCase):
    def test_c(self):
        self.assertTrue('FOO'.isupper())
    def test_d(self):
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()