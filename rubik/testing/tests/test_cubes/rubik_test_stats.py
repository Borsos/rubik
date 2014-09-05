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
           'RubikTestInputOutput',
          ]

import numpy as np

from ....cubes import api as cb
from ....shape import Shape
from .... import py23

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestStats(RubikTestCase):
    METHOD_NAMES = []

    def impl_stats_file(self, shape, dtype, buffer_size=None):
        dtype = cb.get_dtype(dtype)
        shape = Shape(shape)
        file_format = 'raw'
        filename_format = "stats_{shape}_{dtype}.{format}"
        filename = filename_format.format(shape=shape, dtype=dtype, format=file_format)
        dmin = 3
        for d in shape:
            assert d >= dmin, "d={} < {}".format(d, dmin)
        cube_max_index = tuple(0 for i in shape)
        cube_min_index = tuple(1 for i in shape)
        cube_zero_index = tuple(2 for i in shape)
        cube_value = 1.0
        cube_max = 10.0
        cube_min = -23.0
        cube_zero = 0.0
        cube_sum = cube_max + cube_min + cube_value * (shape.count() - dmin)
        cube_ave = cube_sum / float(shape.count())
        cube = cb.const_cube(shape=shape, dtype=dtype, value=cube_value)
        cube[cube_max_index] = cube_max
        cube[cube_min_index] = cube_min
        cube[cube_zero_index] = cube_zero
        cube_count_zero = 1
        cube_count_nonzero = shape.count() - cube_count_zero
        cube_count_nan = 0
        cube_count_inf = 0

        stats_info_cube = cb.stats_info(cube)

        self.assertEqual(stats_info_cube.cube_sum, cube_sum)
        self.assertEqual(stats_info_cube.cube_ave, cube_ave)
        self.assertEqual(stats_info_cube.cube_max, cube_max)
        self.assertEqual(stats_info_cube.cube_min, cube_min)
        self.assertEqual(stats_info_cube.cube_max_index, cube_max_index)
        self.assertEqual(stats_info_cube.cube_min_index, cube_min_index)
        self.assertEqual(stats_info_cube.cube_count_zero, cube_count_zero)
        self.assertEqual(stats_info_cube.cube_count_nonzero, cube_count_nonzero)
        self.assertEqual(stats_info_cube.cube_count_nan, cube_count_nan)
        self.assertEqual(stats_info_cube.cube_count_inf, cube_count_inf)

        cube.tofile(filename)
        self.assertFileExistsAndHasShape(filename, shape=shape, dtype=dtype)

        stats_info_oc = cb.stats_file(filename, shape=shape, dtype=dtype, file_format=file_format,
                                      out_of_core=False)
       
        self.assertEqual(stats_info_oc, stats_info_cube)

        if buffer_size is None:
            total_size = shape.count() * dtype().itemsize
            buffer_size = total_size // 4
        stats_info_ooc = cb.stats_file(filename, shape=shape, dtype=dtype, file_format=file_format,
                                       out_of_core=True, progress_frequency=-1.0, buffer_size=buffer_size)
       
        self.assertEqual(stats_info_ooc, stats_info_cube)

    ### buffer size

    # 4x4, float32, buffer_size=(total_size // 2)
    @testmethod
    def stats_file_4x4_2chunks(self):
        dtype = np.float32
        shape = Shape("4x4")
        self.impl_stats_file(shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 2)

    # 4x4, float64, buffer_size=(total_size // 3)
    @testmethod
    def stats_file_4x4_2chunks(self):
        dtype = np.float64
        shape = Shape("4x4")
        self.impl_stats_file(shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 3)

    # 12x8x19x5, float32, buffer_size=(total_size // 2)
    @testmethod
    def stats_file_12x8x19x5_2chunks(self):
        dtype = np.float32
        shape = Shape("12x8x19x5")
        self.impl_stats_file(shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 2)

    # 12x8x19x5, float64, buffer_size=(total_size // 3)
    @testmethod
    def stats_file_12x8x19x5_2chunks(self):
        dtype = np.float64
        shape = Shape("12x8x19x5")
        self.impl_stats_file(shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 3)

