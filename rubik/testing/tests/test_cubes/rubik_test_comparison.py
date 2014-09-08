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
           'RubikTestComparison',
          ]

import numpy as np

from ....cubes import api as cb
from ....shape import Shape
from .... import py23

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestComparison(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        self.shape = Shape("3x4x5")
        self.l0 = cb.linear_cube(self.shape, start=0.5, increment=1.5)
        self.l1 = cb.linear_cube(self.shape, start=0.5, increment=0.5)
        self.l2 = cb.linear_cube(self.shape, start=-1.0, increment=0.5)

    # tolerance 0.0
    @testmethod
    def not_equals_cube_t0(self):
        cube = cb.not_equals_cube(self.l0, self.l1, tolerance=0.0)
        self.assertFalse(cube[0, 0, 0])
        self.assertEqual(cube.sum(), self.shape.count() - 1)

    @testmethod
    def equals_cube_t0(self):
        cube = cb.equals_cube(self.l0, self.l1, tolerance=0.0)
        self.assertTrue(cube[0, 0, 0])
        self.assertEqual(cube.sum(), 1)

    @testmethod
    def not_equals_num_t0(self):
        num = cb.not_equals_num(self.l0, self.l1, tolerance=0.0)
        self.assertEqual(num, self.shape.count() - 1)

    @testmethod
    def equals_num_t0(self):
        num = cb.equals_num(self.l0, self.l1, tolerance=0.0)
        self.assertEqual(num, 1)

    @testmethod
    def not_equals_t0(self):
        self.assertTrue(cb.not_equals(self.l0, self.l1, tolerance=0.0))

    @testmethod
    def equals_t0(self):
        self.assertFalse(cb.equals(self.l0, self.l1, tolerance=0.0))

    # tolerance 2.0
    @testmethod
    def not_equals_cube_t2(self):
        cube = cb.not_equals_cube(self.l0, self.l1, tolerance=2.0)
        self.assertFalse(cube[0, 0, 0])
        self.assertFalse(cube[0, 0, 1])
        self.assertFalse(cube[0, 0, 2])
        self.assertEqual(cube.sum(), self.shape.count() - 3)

    @testmethod
    def equals_cube_t2(self):
        cube = cb.equals_cube(self.l0, self.l1, tolerance=2.0)
        self.assertTrue(cube[0, 0, 0])
        self.assertTrue(cube[0, 0, 1])
        self.assertTrue(cube[0, 0, 2])
        self.assertEqual(cube.sum(), 3)

    @testmethod
    def not_equals_num_t2(self):
        num = cb.not_equals_num(self.l0, self.l1, tolerance=2.0)
        self.assertEqual(num, self.shape.count() - 3)

    @testmethod
    def equals_num_t2(self):
        num = cb.equals_num(self.l0, self.l1, tolerance=2.0)
        self.assertEqual(num, 3)

    @testmethod
    def not_equals_t2(self):
        self.assertTrue(cb.not_equals(self.l0, self.l1, tolerance=2.0))

    @testmethod
    def equals_t2(self):
        self.assertFalse(cb.equals(self.l0, self.l1, tolerance=2.0))

    # tolerance 10000.0
    @testmethod
    def not_equals_t10000(self):
        self.assertFalse(cb.not_equals(self.l0, self.l1, tolerance=10000.0))

    @testmethod
    def equals_t10000(self):
        self.assertTrue(cb.equals(self.l0, self.l1, tolerance=10000.0))

    # threshold
    @testmethod
    def threshold_cube_3(self):
        cube = cb.threshold_cube(self.l0, 3.0, value=-9.0)
        self.assertEqual(cube[0, 0, 0], -9.0)			# 0.5
        self.assertEqual(cube[0, 0, 1], -9.0)			# 2.0
        self.assertEqual(cube[0, 0, 2], self.l0[0, 0, 2])	# 3.5

    @testmethod
    def threshold_cube_1(self):
        cube = cb.threshold_cube(self.l0, 1.0, value=-9.0)
        self.assertEqual(cube[0, 0, 0], -9.0)			# 0.5
        self.assertEqual(cube[0, 0, 1], self.l0[0, 0, 1])	# 2.0

    @testmethod
    def threshold_cube_0(self):
        cube = cb.threshold_cube(self.l2, value=-9.0)
        self.assertEqual(cube[0, 0, 0], -9.0)			# -1.0
        self.assertEqual(cube[0, 0, 1], -9.0)			# -0.5
        self.assertEqual(cube[0, 0, 2], -9.0)			#  0.0
        self.assertEqual(cube[0, 0, 3], self.l2[0, 0, 3])	#  0.5

    # threshold
    @testmethod
    def abs_threshold_cube_0p6(self):
        cube = cb.abs_threshold_cube(self.l2, 0.6, value=-9.0)
        self.assertEqual(cube[0, 0, 0], self.l2[0, 0, 0])	# -1.0
        self.assertEqual(cube[0, 0, 1], -9.0)			# -0.5
        self.assertEqual(cube[0, 0, 2], -9.0)			#  0.0
        self.assertEqual(cube[0, 0, 3], -9.0)			#  0.5
        self.assertEqual(cube[0, 0, 4], self.l2[0, 0, 4]) 	#  1.0

