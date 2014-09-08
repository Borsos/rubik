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

        self.epsilon = 1.0e-8
        e = self.epsilon
        self.c0 = np.array(
                           [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],
                          )
        self.c1 = np.array(
                           [0.0,   e, 0.0, 1.0,     1.0, 1.0 + e]
                          )
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

    # abs_diff_cube
        # self.c0:
        # [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],

        # self.c1:
        # [0.0,   e, 0.0, 1.0,     1.0, 1.0 + e]

    @testmethod
    def abs_diff_cube_t0(self):
        e = self.epsilon
        cube = cb.abs_diff_cube(self.c0, self.c1)
        cube_cmp = np.array([0.0, e, e, 0.0, e, e])
        for v0, v1 in zip(self.c0, self.c1):
            self.assertAlmostEqual(v0, v1)

    @testmethod
    def abs_diff_cube_inTn6(self):
        e = self.epsilon
        cube = cb.abs_diff_cube(self.c0, self.c1, in_threshold=1e-6)
        cube_cmp = np.array([0.0, 0.0, 0.0, 0.0, e, e])
        for v0, v1 in zip(self.c0, self.c1):
            self.assertAlmostEqual(v0, v1)

    @testmethod
    def abs_diff_cube_outTn6(self):
        e = self.epsilon
        cube = cb.abs_diff_cube(self.c0, self.c1, out_threshold=1e-6)
        cube_cmp = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        for v0, v1 in zip(self.c0, self.c1):
            self.assertAlmostEqual(v0, v1)

    @testmethod
    def abs_diff_cube_inTn6_outTn6(self):
        e = self.epsilon
        cube = cb.abs_diff_cube(self.c0, self.c1, in_threshold=1e-6, out_threshold=1e-6)
        cube_cmp = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        for v0, v1 in zip(self.c0, self.c1):
            self.assertAlmostEqual(v0, v1)

    # rel_diff_cube
        # self.c0:
        # [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],

        # self.c1:
        # [0.0,   e, 0.0, 1.0,     1.0, 1.0 + e]

    @testmethod
    def rel_diff_cube_t0(self):
        e = self.epsilon
        cube = cb.rel_diff_cube(self.c0, self.c1)
        self.assertEqual(cube[0], 0.0)
        self.assertGreater(cube[1], 1.0e30)
        self.assertGreater(cube[2], 0.0)
        self.assertAlmostEqual(cube[3], e / (1.0 + e))
        self.assertAlmostEqual(cube[4], e)

    @testmethod
    def rel_diff_cube_inTn6(self):
        e = self.epsilon
        cube = cb.rel_diff_cube(self.c0, self.c1, in_threshold=1e-6)
        self.assertEqual(cube[0], 0.0)
        self.assertEqual(cube[1], 0.0)
        self.assertEqual(cube[2], 0.0)
        self.assertAlmostEqual(cube[3], e / (1.0 + e))
        self.assertAlmostEqual(cube[4], e)

    @testmethod
    def rel_diff_cube_outTn6(self):
        e = self.epsilon
        cube = cb.rel_diff_cube(self.c0, self.c1, out_threshold=1e-6)
        self.assertEqual(cube[0], 0.0)
        self.assertGreater(cube[1], 1.0e30)
        self.assertGreater(cube[2], 0.0)
        self.assertEqual(cube[3], 0.0)
        self.assertEqual(cube[4], 0.0)

    @testmethod
    def rel_diff_cube_inTn6_outTn6(self):
        e = self.epsilon
        cube = cb.rel_diff_cube(self.c0, self.c1, in_threshold=1e-6, out_threshold=1e-6)
        self.assertEqual(cube[0], 0.0)
        self.assertEqual(cube[1], 0.0)
        self.assertEqual(cube[2], 0.0)
        self.assertEqual(cube[3], 0.0)
        self.assertEqual(cube[4], 0.0)

    @testmethod
    def rel_diff_cube_fraction(self):
        c0 = np.array([2.0])
        c1 = np.array([1.0])
        cube = cb.rel_diff_cube(c0, c1)
        self.assertAlmostEqual(cube[0], 0.5)

    @testmethod
    def rel_diff_cube_percentage(self):
        c0 = np.array([2.0])
        c1 = np.array([1.0])
        cube = cb.rel_diff_cube(c0, c1, percentage=True)
        self.assertAlmostEqual(cube[0], 50.0)

    @testmethod
    def zero_cube(self):
        #c0: [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],
        cube = cb.zero_cube(self.c0)
        cube_cmp = np.array([True, True, False, False, False, False])
        for v0, v1 in zip(cube, cube_cmp):
            self.assertEqual(v0, v1)

    @testmethod
    def zero_cube_Tn6(self):
        #c0: [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],
        cube = cb.zero_cube(self.c0, tolerance=1e-6)
        cube_cmp = np.array([True, True, True, False, False, False])
        for v0, v1 in zip(cube, cube_cmp):
            self.assertEqual(v0, v1)
      
        
    @testmethod
    def nonzero_cube(self):
        #c0: [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],
        cube = cb.nonzero_cube(self.c0)
        cube_cmp = np.array([True, True, False, False, False, False])
        for v0, v1 in zip(cube, cube_cmp):
            self.assertEqual(v0, not v1)

    @testmethod
    def nonzero_cube_Tn6(self):
        #c0: [0.0, 0.0,   e, 1.0, 1.0 + e,     1.0],
        cube = cb.nonzero_cube(self.c0, tolerance=1e-6)
        cube_cmp = np.array([True, True, True, False, False, False])
        for v0, v1 in zip(cube, cube_cmp):
            self.assertEqual(v0, not v1)

    @testmethod
    def where_indices(self):
        a = np.eye(3)
        a[1, 2] = -2.0
        a[2, 1] =  2.0
        cube = cb.where_indices(a)
        self.assertEqual(cube.shape, (5, 3))
        self.assertCubesAreEqual(cube[0], np.array([0.0, 0.0,  1.0]))
        self.assertCubesAreEqual(cube[1], np.array([1.0, 1.0,  1.0]))
        self.assertCubesAreEqual(cube[2], np.array([1.0, 2.0, -2.0]))
        self.assertCubesAreEqual(cube[3], np.array([2.0, 1.0,  2.0]))
        self.assertCubesAreEqual(cube[4], np.array([2.0, 2.0,  1.0]))

    @testmethod
    def where_indices_condition(self):
        a = np.eye(3)
        a[1, 2] = -2.0
        a[2, 1] =  2.0
        cube = cb.where_indices(a, np.abs(a) > 1.0)
        self.assertEqual(cube.shape, (2, 3))
        self.assertCubesAreEqual(cube[0], np.array([1.0, 2.0, -2.0]))
        self.assertCubesAreEqual(cube[1], np.array([2.0, 1.0,  2.0]))
      
        
