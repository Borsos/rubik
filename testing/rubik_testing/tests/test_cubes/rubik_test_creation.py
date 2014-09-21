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
           'RubikTestCreation',
          ]

import numpy as np

from rubik.cubes import api as cb
from rubik.shape import Shape

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestCreation(RubikTestCase):
    METHOD_NAMES = []

    ##### random cube
    def impl_random_cube(self, shape, dtype, min, max):
        dtype = cb.get_dtype(dtype)
        shape = Shape(shape)
        file_format = 'raw'
        filename_format = "random_{{shape}}_{{dtype}}_{min}_{max}.{{format}}".format(min=min, max=max)
        filename = filename_format.format(shape=shape, dtype=dtype, format=file_format)
        cube = cb.random_cube(shape=shape, dtype=dtype, min=min, max=max)
        
        cube_min = cube.min()
        cube_max = cube.max()
        self.assertGreaterEqual(cube_min, min)
        self.assertLessEqual(cube_max, max)
        self.assertEqual(dtype, cube.dtype.type)

    ## random cube, 3x5x6, float32, min=0, max=1
    @testmethod
    def random_cube_3x5x6_float32_0_1(self):
        return self.impl_random_cube(shape="3x5x6", dtype="float32", min=0.0, max=1.0)

    ## random cube, 3x5x6, float64, min=0.0, max=1.0
    @testmethod
    def random_cube_3x5x6_float64_0_1(self):
        return self.impl_random_cube(shape="3x5x6", dtype="float64", min=0.0, max=1.0)

    ## random cube, 3x5x6, int32, min=0.0, max=1.0
    @testmethod
    def random_cube_3x5x6_int32_0_1(self):
        return self.impl_random_cube(shape="3x5x6", dtype="int32", min=0.0, max=1.0)

    ## random cube, 18x19, float32, min=100.0, max=200.0
    @testmethod
    def random_cube_18x19_float32_100_200(self):
        return self.impl_random_cube(shape="18x19", dtype="float32", min=100.0, max=200.0)

    ## random cube, 18x19, float32, min=-300.0, max=-100.0
    @testmethod
    def random_cube_18x19_float32_n300_n100(self):
        return self.impl_random_cube(shape="18x19", dtype="float32", min=-300.0, max=100.0)

    ##### const cube
    def impl_const_cube(self, shape, dtype, value):
        dtype = cb.get_dtype(dtype)
        shape = Shape(shape)
        file_format = 'raw'
        filename_format = "const_{{shape}}_{{dtype}}_{value}.{{format}}".format(value=value)
        filename = filename_format.format(shape=shape, dtype=dtype, format=file_format)
        cube = cb.const_cube(shape=shape, dtype=dtype, value=value)
        
        cube_min = cube.min()
        cube_max = cube.max()
        self.assertEqual(cube_min, value)
        self.assertEqual(cube_max, value)
        self.assertEqual(dtype, cube.dtype.type)

    ## const cube, 3x5x6, float32, value=0.0
    @testmethod
    def const_cube_3x5x6_float32_0(self):
        return self.impl_const_cube(shape="3x5x6", dtype="float32", value=0.0)

    ## const cube, 3x5x6, float64, value=0.0
    @testmethod
    def const_cube_3x5x6_float64_0(self):
        return self.impl_const_cube(shape="3x5x6", dtype="float64", value=0.0)

    ## const cube, 3x5x6, int32, value=0
    @testmethod
    def const_cube_3x5x6_int32_0(self):
        return self.impl_const_cube(shape="3x5x6", dtype="int32", value=0)

    ## const cube, 3x5x6, int32, value=-5
    @testmethod
    def const_cube_3x5x6_int32_n5(self):
        return self.impl_const_cube(shape="3x5x6", dtype="int32", value=-5)

    ## const cube, 18x19, float32, value=100.0
    @testmethod
    def const_cube_18x19_float32_100(self):
        return self.impl_const_cube(shape="18x19", dtype="float32", value=100.0)

    ## const cube, 18x19, float32, value=-300.5
    @testmethod
    def const_cube_18x19_float32_n300p5(self):
        return self.impl_const_cube(shape="18x19", dtype="float32", value=-300.5)

    ##### const blocks cube
    def impl_const_blocks_cube(self, shape, dtype, start, increment, const_dims, cmp_cube):
        dtype = cb.get_dtype(dtype)
        shape = Shape(shape)
        file_format = 'raw'
        filename_format = "const_blocks_{{shape}}_{{dtype}}_{start}_{increment}_{const_dims}.{{format}}".format(
            start=start,
            increment=increment,
            const_dims="+".join(repr(d) for d in const_dims),
        )
        filename = filename_format.format(shape=shape, dtype=dtype, format=file_format)
        cube = cb.const_blocks_cube(shape=shape, dtype=dtype,
            start=start, increment=increment, const_dims=const_dims)
        
        cube_min = cube.min()
        cube_max = cube.max()
        self.assertEqual(cube_min, start)
        self.assertEqual(cb.not_equals_num(cube, cmp_cube), 0)

    # 3x2x4, 0.5, 2.5, ()
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_(self):
        cmp_cube = [
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [10.5, 13.0, 15.5, 18.0],
                    ],
                    [
                     [20.5, 23.0, 25.5, 28.0],
                     [30.5, 33.0, 35.5, 38.0],
                    ],
                    [
                     [40.5, 43.0, 45.5, 48.0],
                     [50.5, 53.0, 55.5, 58.0],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(), cmp_cube=cmp_cube)
    
    # 3x2x4, 0.5, 2.5, (0, )
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_0(self):
        cmp_cube = [
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [10.5, 13.0, 15.5, 18.0],
                    ],
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [10.5, 13.0, 15.5, 18.0],
                    ],
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [10.5, 13.0, 15.5, 18.0],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(0, ), cmp_cube=cmp_cube)
    
    # 3x2x4, 0.5, 2.5, (1, )
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_1(self):
        cmp_cube = [
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [ 0.5,  3.0,  5.5,  8.0],
                    ],
                    [
                     [10.5, 13.0, 15.5, 18.0],
                     [10.5, 13.0, 15.5, 18.0],
                    ],
                    [
                     [20.5, 23.0, 25.5, 28.0],
                     [20.5, 23.0, 25.5, 28.0],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(1, ), cmp_cube=cmp_cube)
    
        
    # 3x2x4, 0.5, 2.5, (2, )
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_2(self):
        cmp_cube = [
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 3.0,  3.0,  3.0,  3.0],
                    ],
                    [
                     [ 5.5,  5.5,  5.5,  5.5],
                     [ 8.0,  8.0,  8.0,  8.0],
                    ],
                    [
                     [10.5, 10.5, 10.5, 10.5],
                     [13.0, 13.0, 13.0, 13.0],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(2, ), cmp_cube=cmp_cube)
    
        
    # 3x2x4, 0.5, 2.5, (0, 1)
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_0_1(self):
        cmp_cube = [
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [ 0.5,  3.0,  5.5,  8.0],
                    ],
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [ 0.5,  3.0,  5.5,  8.0],
                    ],
                    [
                     [ 0.5,  3.0,  5.5,  8.0],
                     [ 0.5,  3.0,  5.5,  8.0],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(0, 1), cmp_cube=cmp_cube)
    
    # 3x2x4, 0.5, 2.5, (1, 2)
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_0_2(self):
        cmp_cube = [
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 3.0,  3.0,  3.0,  3.0],
                    ],
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 3.0,  3.0,  3.0,  3.0],
                    ],
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 3.0,  3.0,  3.0,  3.0],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(0, 2), cmp_cube=cmp_cube)
    
    # 3x2x4, 0.5, 2.5, (1, 2)
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_1_2(self):
        cmp_cube = [
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 0.5,  0.5,  0.5,  0.5],
                    ],
                    [
                     [ 3.0,  3.0,  3.0,  3.0],
                     [ 3.0,  3.0,  3.0,  3.0],
                    ],
                    [
                     [ 5.5,  5.5,  5.5,  5.5],
                     [ 5.5,  5.5,  5.5,  5.5],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(1, 2), cmp_cube=cmp_cube)
    
    # 3x2x4, 0.5, 2.5, (0, 1, 2)
    @testmethod
    def const_blocks_cube_3x2x4_0p5_2p5_0_1_2(self):
        cmp_cube = [
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 0.5,  0.5,  0.5,  0.5],
                    ],
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 0.5,  0.5,  0.5,  0.5],
                    ],
                    [
                     [ 0.5,  0.5,  0.5,  0.5],
                     [ 0.5,  0.5,  0.5,  0.5],
                    ],
                   ]
        return self.impl_const_blocks_cube(shape="3x2x4", dtype='float32',
                                           start=0.5, increment=2.5, const_dims=(0, 1, 2), cmp_cube=cmp_cube)
    

    ##### join
    def impl_join(self, cubes, result):
        cube = cb.join(cubes)
        self.assertEqual(cube.shape, result.shape)
        self.assertEqual(cb.not_equals_num(cube, result), 0)

    @testmethod
    def join3(self):
        cube0 = cb.const_cube(shape="3x5", value=1.5)
        cube1 = cb.linear_cube(shape="3x5", start=1.5, increment=0.5)
        cube2 = cb.const_cube(shape="3x5", value=-1.5)
        cubes = (cube0, cube1, cube2)
        result = np.array(cubes)
        return self.impl_join(cubes, result)
