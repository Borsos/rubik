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

from ..shape import Shape
from ..cubes import internals
from ..cubes import api as cb

class RubikTestCase(unittest.TestCase):
    def assertFileExists(self, filename):
        self.assertTrue(os.path.exists(filename))

    def assertFileExistsAndHasSize(self, filename, size):
        self.assertFileExists(filename)
        self.assertTrue(os.stat(filename).st_size == size)

    def assertFileExistsAndHasShape(self, filename, shape, dtype=None):
        if dtype is None:
            dtype = internals.get_default_dtype()
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        size = shape.count() * dtype().itemsize
        self.assertFileExistsAndHasSize(filename, size)
