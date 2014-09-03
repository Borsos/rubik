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
           'RubikTestCubes',
          ]

import numpy as np

from ....cubes import api as cb
from ....shape import Shape

from ...rubik_test_case import RubikTestCase

class RubikTestCubes(RubikTestCase):
    def runTest_WriteRawOutOfCore(self):
        filename_format_a = "a_{shape}_{dtype}.{format}"
        filename_format_b = "b_{shape}_{dtype}.{format}"
        for shape_s in "85x70x40", "4", "1x2":
            shape = Shape(shape_s)
            for dtype in np.float32, np.float64, np.int32, np.int64:
                cb.write_random_cube(filename_format_a, shape=shape, dtype=dtype)
                filename_a = filename_format_a.format(
                    shape=shape,
                    dtype=dtype.__name__,
                    format='raw',
                )
                self.assertFileExistsAndHasShape(filename_a, shape=shape, dtype=dtype)
                cube = cb.fromfile_raw(filename_format_a, shape=shape, dtype=dtype)
                self.assertTrue(cube.dtype == dtype)
                self.assertEqual(cube.size, shape.count())

                filename_b = filename_format_b.format(
                    shape=shape,
                    dtype=dtype.__name__,
                    format='raw',
                )
                cube.tofile(filename_b)
                self.assertFilesAreEqual(filename_a, filename_b)
