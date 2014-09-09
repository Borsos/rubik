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
from ....cubes import utilities
from ....shape import Shape
from .... import py23

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestInputOutput(RubikTestCase):
    METHOD_NAMES = []

    def impl_write_cube_out_of_core(self, kind, shape, dtype, buffer_size=None):
        dtype = utilities.get_dtype(dtype)
        shape = Shape(shape)
        filename_format_a = "a_{kind}_{{shape}}_{{dtype}}.{{format}}".format(kind=kind)
        filename_format_b = "b_{kind}_{{shape}}_{{dtype}}.{{format}}".format(kind=kind)
        filename_format_c = "c_{kind}_{{shape}}_{{dtype}}.{{format}}".format(kind=kind)
        if issubclass(dtype, np.integer):
            l_start = dtype(3)
            l_increment = dtype(2)
            c_value = dtype(7)
        else:
            l_start = dtype(0.5)
            l_increment = dtype(1.5)
            c_value = dtype(7.5)
        p_args = []
        n_args = {}
        if kind == 'random':
            ooc_function = cb.write_random_cube
            oc_function = cb.random_cube
        elif kind == 'linear':
            ooc_function = cb.write_linear_cube
            oc_function = cb.linear_cube
            n_args['start'] = l_start
            n_args['increment'] = l_increment
        elif kind == 'const':
            ooc_function = cb.write_const_cube
            oc_function = cb.const_cube
            n_args['value'] = c_value
        else:
            assert False, kind
        cb.set_random_seed(10)
        ooc_function(filename_format_a, shape=shape, dtype=dtype, *p_args, **n_args)
        filename_a = filename_format_a.format(
            shape=shape,
            dtype=dtype.__name__,
            format='raw',
        )
        self.assertFileExistsAndHasShape(filename_a, shape=shape, dtype=dtype)
        ooc_cube = cb.read_cube_raw(filename_format_a, shape=shape, dtype=dtype)
        self.assertTrue(ooc_cube.dtype == dtype)
        self.assertEqual(ooc_cube.size, shape.count())

        cb.set_random_seed(10)
        oc_cube = oc_function(shape=shape, dtype=dtype, *p_args, **n_args)
        self.assertCubesAreEqual(ooc_cube, oc_cube)

        if kind == 'random':
            pass
        elif kind == 'linear':
            #     0) start +    0 * increment
            #     1) start +    1 * increment
            #     2) start +    2 * increment
            #     3) start +    3 * increment
            #        ...
            # count) start + count * increment
            # ==    (start * count) + (((count - 1) * count) // 2) * increment
            count = shape.count()
            sum_count = ((count - 1) * count) // 2
            l_sum = (l_start * count) + (l_increment * sum_count)
            self.assertEqual(cb.precise_sum(ooc_cube), l_sum)
        elif kind == 'const':
            self.assertEqual(cb.precise_sum(ooc_cube), shape.count() * c_value)
        filename_b = filename_format_b.format(
            shape=shape,
            dtype=dtype.__name__,
            format='raw',
        )
        ooc_cube.tofile(filename_b)
        self.assertFilesAreEqual(filename_a, filename_b)

    ### buffer size

    # linear, float32, buffer_size=(total_size // 2)
    @testmethod
    def write_linear_cube_out_of_core_4x4_float32(self):
        dtype = np.float32
        shape = Shape("4x4")
        self.impl_write_cube_out_of_core(kind='linear', shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 2)

    # linear, float64, buffer_size=(total_size // 2)
    @testmethod
    def write_linear_cube_out_of_core_4x4_float32(self):
        dtype = np.float32
        shape = Shape("4x4")
        self.impl_write_cube_out_of_core(kind='linear', shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 2)

    # linear, int32, buffer_size=(total_size // 2)
    @testmethod
    def write_linear_cube_out_of_core_4x4_int32(self):
        dtype = np.int32
        shape = Shape("4x4")
        self.impl_write_cube_out_of_core(kind='linear', shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 2)

    # linear, int64, buffer_size=(total_size // 2)
    @testmethod
    def write_linear_cube_out_of_core_4x4_int32(self):
        dtype = np.int32
        shape = Shape("4x4")
        self.impl_write_cube_out_of_core(kind='linear', shape=shape, dtype=dtype, buffer_size=shape.count() * dtype().itemsize / 2)

    ###

    # random, float32
    @testmethod
    def write_random_cube_out_of_core_20x20x10_float32(self):
        self.impl_write_cube_out_of_core(kind='random', shape='20x20x10', dtype='float32')

    @testmethod
    def write_random_cube_out_of_core_4_float32(self):
        self.impl_write_cube_out_of_core(kind='random', shape='4', dtype='float32')

    @testmethod
    def write_random_cube_out_of_core_1x2_float32(self):
        self.impl_write_cube_out_of_core(kind='random', shape='1x2', dtype='float32')

    # random, float64
    @testmethod
    def write_random_cube_out_of_core_85x70x40_float64(self):
        self.impl_write_cube_out_of_core(kind='random', shape='85x70x40', dtype='float64')

    @testmethod
    def write_random_cube_out_of_core_4_float64(self):
        self.impl_write_cube_out_of_core(kind='random', shape='4', dtype='float64')

    @testmethod
    def write_random_cube_out_of_core_1x2_float64(self):
        self.impl_write_cube_out_of_core(kind='random', shape='1x2', dtype='float64')

    # random, int32
    @testmethod
    def write_random_cube_out_of_core_20x20x10_int32(self):
        self.impl_write_cube_out_of_core(kind='random', shape='20x20x10', dtype='int32')

    @testmethod
    def write_random_cube_out_of_core_4_int32(self):
        self.impl_write_cube_out_of_core(kind='random', shape='4', dtype='int32')

    @testmethod
    def write_random_cube_out_of_core_1x2_int32(self):
        self.impl_write_cube_out_of_core(kind='random', shape='1x2', dtype='int32')

    # random, int64
    @testmethod
    def write_random_cube_out_of_core_85x70x40_int64(self):
        self.impl_write_cube_out_of_core(kind='random', shape='85x70x40', dtype='int64')

    @testmethod
    def write_random_cube_out_of_core_4_int64(self):
        self.impl_write_cube_out_of_core(kind='random', shape='4', dtype='int64')

    @testmethod
    def write_random_cube_out_of_core_1x2_int64(self):
        self.impl_write_cube_out_of_core(kind='random', shape='1x2', dtype='int64')

    # linear, float32
    @testmethod
    def write_linear_cube_out_of_core_20x20x10_float32(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='20x20x10', dtype='float32')

    @testmethod
    def write_linear_cube_out_of_core_4_float32(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='4', dtype='float32')

    @testmethod
    def write_linear_cube_out_of_core_1x2_float32(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='1x2', dtype='float32')

    # linear, float64
    @testmethod
    def write_linear_cube_out_of_core_85x70x40_float64(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='85x70x40', dtype='float64')

    @testmethod
    def write_linear_cube_out_of_core_4_float64(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='4', dtype='float64')

    @testmethod
    def write_linear_cube_out_of_core_1x2_float64(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='1x2', dtype='float64')

    # linear, int32
    @testmethod
    def write_linear_cube_out_of_core_20x20x10_int32(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='20x20x10', dtype='int32')

    @testmethod
    def write_linear_cube_out_of_core_4_int32(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='4', dtype='int32')

    @testmethod
    def write_linear_cube_out_of_core_1x2_int32(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='1x2', dtype='int32')

    # linear, int64
    @testmethod
    def write_linear_cube_out_of_core_85x70x40_int64(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='85x70x40', dtype='int64')

    @testmethod
    def write_linear_cube_out_of_core_4_int64(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='4', dtype='int64')

    @testmethod
    def write_linear_cube_out_of_core_1x2_int64(self):
        self.impl_write_cube_out_of_core(kind='linear', shape='1x2', dtype='int64')

    # const, float32
    @testmethod
    def write_const_cube_out_of_core_20x20x10_float32(self):
        self.impl_write_cube_out_of_core(kind='const', shape='20x20x10', dtype='float32')

    @testmethod
    def write_const_cube_out_of_core_4_float32(self):
        self.impl_write_cube_out_of_core(kind='const', shape='4', dtype='float32')

    @testmethod
    def write_const_cube_out_of_core_1x2_float32(self):
        self.impl_write_cube_out_of_core(kind='const', shape='1x2', dtype='float32')

    # const, float64
    @testmethod
    def write_const_cube_out_of_core_85x70x40_float64(self):
        self.impl_write_cube_out_of_core(kind='const', shape='85x70x40', dtype='float64')

    @testmethod
    def write_const_cube_out_of_core_4_float64(self):
        self.impl_write_cube_out_of_core(kind='const', shape='4', dtype='float64')

    @testmethod
    def write_const_cube_out_of_core_1x2_float64(self):
        self.impl_write_cube_out_of_core(kind='const', shape='1x2', dtype='float64')

    # const, int32
    @testmethod
    def write_const_cube_out_of_core_20x20x10_int32(self):
        self.impl_write_cube_out_of_core(kind='const', shape='20x20x10', dtype='int32')

    @testmethod
    def write_const_cube_out_of_core_4_int32(self):
        self.impl_write_cube_out_of_core(kind='const', shape='4', dtype='int32')

    @testmethod
    def write_const_cube_out_of_core_1x2_int32(self):
        self.impl_write_cube_out_of_core(kind='const', shape='1x2', dtype='int32')

    # const, int64
    @testmethod
    def write_const_cube_out_of_core_85x70x40_int64(self):
        self.impl_write_cube_out_of_core(kind='const', shape='85x70x40', dtype='int64')

    @testmethod
    def write_const_cube_out_of_core_4_int64(self):
        self.impl_write_cube_out_of_core(kind='const', shape='4', dtype='int64')

    @testmethod
    def write_const_cube_out_of_core_1x2_int64(self):
        self.impl_write_cube_out_of_core(kind='const', shape='1x2', dtype='int64')

