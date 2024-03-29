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

class RubikTestHistogram(RubikTestCase):
    METHOD_NAMES = []

    def impl_histogram(self, shape, dtype, hlength, bins, mode): 
        dtype = cb.get_dtype(dtype)
        shape = Shape(shape)
        cube = cb.random_cube(shape=shape, dtype=dtype)
        output_lines = cb.histogram(cube, hlength=hlength, bins=bins, mode=mode)
        self.assertEqual(len(output_lines), bins)
        for line in output_lines:
            self.assertEqual(len(line), hlength)

    @testmethod
    def histogram_4x4_float32_80_10_number(self):
        self.impl_histogram("4x4", "float32", hlength=80, bins=10, mode='number')
        
    @testmethod
    def histogram_4x4_float32_80_10_percentage(self):
        self.impl_histogram("4x4", "float32", hlength=80, bins=10, mode='percentage')
        
    @testmethod
    def histogram_4x4_float32_30_17_number(self):
        self.impl_histogram("4x4", "float32", hlength=30, bins=17, mode='number')
        
    @testmethod
    def histogram_4x4_float32_30_17_percentage(self):
        self.impl_histogram("4x4", "float32", hlength=30, bins=17, mode='percentage')
        
    @testmethod
    def histogram_4x4_int64_80_101_number(self):
        self.impl_histogram("4x4", "int64", hlength=80, bins=101, mode='number')
        
    @testmethod
    def histogram_4x4_int64_80_101_percentage(self):
        self.impl_histogram("4x4", "int64", hlength=80, bins=101, mode='percentage')
        
