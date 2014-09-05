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
import fnmatch
import inspect
import os

import numpy as np

from ..units import Memory
from ..shape import Shape
from ..cubes import internals
from ..cubes import api as cb
from .rubik_test_conf import RUBIK_TEST_CONF

def testmethod(method):
    stack = inspect.stack()
    frame, filename, line_number, function_name, lines, index = stack[1]
    method_list = frame.f_locals['METHOD_NAMES']
    method_list.append(method.__name__)
    return method
    
class RubikTestCase(unittest.TestCase):
    METHOD_NAMES = []
    def __init__(self, test_name):
        self.test_name = test_name
        # test_name can be:
        #  o 'test'
        #  o 'test_class'.'test'
        #  o 'suite_name'.'test_class'.'test'
        method_name = self.test_name.split('.')[-1]
        super(RubikTestCase, self).__init__(methodName=method_name)
        self.logger = RUBIK_TEST_CONF.logger

    @classmethod
    def class_name(cls):
        class_name = cls.__name__
        class_name_prefix = "RubikTest"
        if class_name.startswith(class_name_prefix):
            class_name = class_name[len(class_name_prefix):]
        return class_name

    @classmethod
    def test_names(cls):
        class_name = cls.class_name()
        for test_method in cls.METHOD_NAMES:
            test_name = "{}.{}".format(class_name, test_method)
            yield test_name

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

    def assertCubesAreEqual(self, cube_a, cube_b):
        if cb.not_equals_num(cube_a, cube_b) != 0:
            raise AssertionError("cubes {} and {} differ".format(
                cube_a.shape,
                cube_b.shape))

    def assertCubesDiffer(self, cube_a, cube_b):
        if cb.equals_num(cube_a, cube_b) != 0:
            raise AssertionError("cubes {} and {} are identical".format(
                cube_a.shape,
                cube_b.shape))

    def assertAlmostEqualStatsInfo(self, stats_info_a, stats_info_b):
        for key in cb.StatsInfo.get_keys():
            value_a = getattr(stats_info_a, key)
            value_b = getattr(stats_info_b, key)
            try:
               self.assertAlmostEqual(value_a, value_b)
            except AssertionError:
               raise AssertionError("stats_info key {!r} differ: {!r} != {!r}".format(key, value_a, value_b))

    def assertAlmostEqualDiffInfo(self, diff_info_a, diff_info_b):
        for stats_info_key in 'left', 'right', 'abs_diff', 'rel_diff':
            stats_info_a = getattr(diff_info_a, stats_info_key)
            stats_info_b = getattr(diff_info_b, stats_info_key)
            for key in cb.StatsInfo.get_keys():
                value_a = getattr(stats_info_a, key)
                value_b = getattr(stats_info_b, key)
                try:
                   self.assertAlmostEqual(value_a, value_b)
                except AssertionError:
                   raise AssertionError("diff_info {!r}: stats_info key {!r} differ: {!r} != {!r}".format(stats_info_key, key, value_a, value_b))

