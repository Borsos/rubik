#!/usr/bin/env python3
#
# Copyright 2014 Simone Campagna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = "Simone Campagna"

__all__ = [
           'RubikTestCase',
          ]


import unittest
import os

from ..units import Memory
from ..shape import Shape
from ..cubes import internals

class RubikTestCase(unittest.TestCase):
    @classmethod
    def register(cls, suite):
        for member in dir(cls):
            if member.startswith("runTest_"):
                suite.addTest(cls(methodName=member))

    def assertPathExists(self, filename):
        if not os.path.exists(filename):
            raise AssertionError("path {!r} does not exists".format(filename))
            
    def assertFileExists(self, filename):
        self.assertPathExists(filename)
        if not os.path.isfile(filename):
            raise AssertionError("path {!r} is not a file".format(filename))

    def assertDirExists(self, filename):
        self.assertPathExists(filename)
        if not os.path.isdir(filename):
            raise AssertionError("path {!r} is not a directory".format(filename))

    def assertFileExistsAndHasSize(self, filename, size):
        self.assertFileExists(filename)
        filesize = os.stat(filename).st_size
        if filesize != size:
            raise AssertionError("file {!r} has size {} != {}".format(filename, filesize, size))

    def assertFileExistsAndHasShape(self, filename, shape, dtype=None):
        self.assertFileExists(filename)
        if dtype is None:
            dtype = internals.get_default_dtype()
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        size = shape.count() * dtype().itemsize
        filesize = os.stat(filename).st_size
        if filesize != size:
            raise AssertionError("file {!r} has size {} != {} [shape={}, dtype={}]".format(filename, filesize, size, shape, dtype.__name__))

    def compare_files(self, filename_a, filename_b):
        block_bytes = Memory('1gb').get_bytes()
        offset = 0
        with open(filename_a, 'rb') as f_a, open(filename_b, 'rb') as f_b:
            block_a = f_a.read(block_bytes)
            block_b = f_b.read(block_bytes)
            if block_a != block_b:
                for count, (ca, cb) in enumerate(zip(block_a, block_b)):
                    if ca != cb:
                        return False, offset + count
            offset += len(block_a)
        return True, -1

    def assertFilesAreEqual(self, filename_a, filename_b):
        self.assertFileExists(filename_a)
        size = os.stat(filename_a).st_size
        self.assertFileExistsAndHasSize(filename_b, size)
        match, offset = self.compare_files(filename_a, filename_b)
        if not match:
            raise AssertionError("file {!r} differs from file {!r}; first difference at {}".format(
                filename_a,
                filename_b,
                offset))

    def assertFilesDiffer(self, filename_a, filename_b):
        self.assertFileExists(filename_a)
        size = os.stat(filename_a).st_size
        self.assertFileExistsAndHasSize(filename_b, size)
        match, offset = self.compare_files(filename_a, filename_b)
        if match:
            raise AssertionError("files {!r} and {!r} are identical".format(
                filename_a,
                filename_b))
