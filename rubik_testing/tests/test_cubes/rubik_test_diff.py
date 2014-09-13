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

from rubik.cubes import api as cb
from rubik.shape import Shape

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestDiff(RubikTestCase):
    METHOD_NAMES = []

    def create_random_cubes(self, shape, dtype):
        cube_l = cb.random_cube(shape=shape, dtype=dtype)
        cube_r = cube_l * 1.5
        dmin = 2
        for d in shape:
            assert d >= dmin, "d={} < {}".format(d, dmin)
        index_diff_0 = tuple(0 for i in shape)
        index_diff_1 = tuple(1 for i in shape)
        cube_r[index_diff_0] = cube_l[index_diff_0] * 0.1
        cube_r[index_diff_1] = cube_l[index_diff_1] * 10.3

        return cube_l, cube_r

    def create_linear_cubes(self, shape, dtype):
        cube_l = cb.linear_cube(shape=shape, dtype=dtype)
        cube_r = cube_l * 1.5
        dmin = 2
        for d in shape:
            assert d >= dmin, "d={} < {}".format(d, dmin)
        index_diff_0 = tuple(0 for i in shape)
        index_diff_1 = tuple(1 for i in shape)
        cube_r[index_diff_0] = cube_l[index_diff_0] * 0.1
        cube_r[index_diff_1] = cube_l[index_diff_1] * 10.3

        return cube_l, cube_r

    def assertAlmostEqualStatsInfo(self, stats_info_a, stats_info_b):
        for key in cb.StatsInfo.get_keys():
            self.assertAlmostEqual(getattr(stats_info_a, key), getattr(stats_info_b, key))

    def diff_cubes(self, kind, shape, dtype, cube_l, cube_r, buffer_size):
        diff_info_cubes = cb.diff_info(cube_l, cube_r)
        stats_info_cube_l = cb.stats_info(cube_l)
        stats_info_cube_r = cb.stats_info(cube_r)
        stats_info_cube_abs = cb.stats_info(cb.abs_diff_cube(cube_l, cube_r))
        stats_info_cube_rel = cb.stats_info(cb.rel_diff_cube(cube_l, cube_r))

        self.assertAlmostEqualStatsInfo(diff_info_cubes.left, stats_info_cube_l)
        self.assertAlmostEqualStatsInfo(diff_info_cubes.right, stats_info_cube_r)
        self.assertAlmostEqualStatsInfo(diff_info_cubes.abs_diff, stats_info_cube_abs)
        self.assertAlmostEqualStatsInfo(diff_info_cubes.rel_diff, stats_info_cube_rel)

        cube_l_filename_format = "cube_l_{kind}_{{shape}}_{{dtype}}.{{format}}".format(kind=kind)
        cube_l_filename = cube_l_filename_format.format(shape=shape, dtype=dtype, format='raw')
        cube_r_filename_format = "cube_r_{kind}_{{shape}}_{{dtype}}.{{format}}".format(kind=kind)
        cube_r_filename = cube_r_filename_format.format(shape=shape, dtype=dtype, format='raw')
        cube_l.tofile(cube_l_filename)
        cube_r.tofile(cube_r_filename)

        diff_info_oc = cb.diff_files(cube_l_filename, cube_r_filename,
            shape=shape,
            dtype=dtype,
            out_of_core=False)

        self.assertEqual(diff_info_oc, diff_info_cubes)
        diff_info_ooc = cb.diff_files(cube_l_filename, cube_r_filename,
            shape=shape,
            dtype=dtype,
            out_of_core=True,
            buffer_size=buffer_size,
            progress_frequency=-1.0)
        self.assertEqual(diff_info_oc, diff_info_cubes)

        diff_info_oc_report = diff_info_oc.report()
        diff_info_ooc_report = diff_info_ooc.report()
        self.assertEqual(diff_info_oc_report, diff_info_ooc_report)

    def get_buffer_size(self, shape, dtype, buffer_size=None, chunks=2):
        if buffer_size is None:
            buffer_size = int(shape.count() * dtype().itemsize / chunks)
        return buffer_size

    def impl_diff_random_files(self, shape, dtype, buffer_size):
        cube_l, cube_r = self.create_random_cubes(shape=shape, dtype=dtype)
        self.diff_cubes(
            kind='random',
            shape=shape,
            dtype=dtype,
            cube_l=cube_l,
            cube_r=cube_r,
            buffer_size=buffer_size)
    
    def impl_diff_linear_files(self, shape, dtype, buffer_size):
        cube_l, cube_r = self.create_linear_cubes(shape=shape, dtype=dtype)
        self.diff_cubes(
            kind='linear',
            shape=shape,
            dtype=dtype,
            cube_l=cube_l,
            cube_r=cube_r,
            buffer_size=buffer_size)
    
    ### tests 

    # random
    # 4x4, float32, buffer_size=(total_size // 2)
    @testmethod
    def diff_random_files_4x4_2chunks(self):
        dtype = np.float32
        shape = Shape("4x4")
        self.impl_diff_random_files(shape=shape, dtype=dtype, 
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=2))

    # 4x4, float64, buffer_size=(total_size // 3)
    @testmethod
    def diff_random_files_4x4_3chunks(self):
        dtype = np.float64
        shape = Shape("4x4")
        self.impl_diff_random_files(shape=shape, dtype=dtype,
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=3))

    # 12x8x19x5, float32, buffer_size=(total_size // 2)
    @testmethod
    def diff_random_files_12x8x19x5_2chunks(self):
        dtype = np.float32
        shape = Shape("12x8x19x5")
        self.impl_diff_random_files(shape=shape, dtype=dtype,
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=2))

    # 12x8x19x5, float64, buffer_size=(total_size // 3)
    @testmethod
    def diff_random_files_12x8x19x5_3chunks(self):
        dtype = np.float64
        shape = Shape("12x8x19x5")
        self.impl_diff_random_files(shape=shape, dtype=dtype,
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=3))

    # const
    # 4x4, float32, buffer_size=(total_size // 2)
    @testmethod
    def diff_linear_files_4x4_2chunks(self):
        dtype = np.float32
        shape = Shape("4x4")
        self.impl_diff_linear_files(shape=shape, dtype=dtype, 
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=2))

    # 4x4, float64, buffer_size=(total_size // 3)
    @testmethod
    def diff_linear_files_4x4_3chunks(self):
        dtype = np.float64
        shape = Shape("4x4")
        self.impl_diff_linear_files(shape=shape, dtype=dtype,
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=3))

    # 12x8x19x5, float32, buffer_size=(total_size // 2)
    @testmethod
    def diff_linear_files_12x8x19x5_2chunks(self):
        dtype = np.float32
        shape = Shape("12x8x19x5")
        self.impl_diff_linear_files(shape=shape, dtype=dtype,
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=2))

    # 12x8x19x5, float64, buffer_size=(total_size // 3)
    @testmethod
    def diff_linear_files_12x8x19x5_3chunks(self):
        dtype = np.float64
        shape = Shape("12x8x19x5")
        self.impl_diff_linear_files(shape=shape, dtype=dtype,
            buffer_size=self.get_buffer_size(shape=shape, dtype=dtype, chunks=3))

