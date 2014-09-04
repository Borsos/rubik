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
           'RubikTestShape',
          ]

from ....shape import Shape

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestShape(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestShape, self).setUp()
        self._shapes = []
        for shape_t in (), (1, ), (2, 4), (3, 5, 4, 6), (10, 30, 10, 40, 20, 33):
            shape_s = 'x'.join(str(d) for d in shape_t)
            if len(shape_t) == 0:
                count = 0
            else:
                count = 1
                for d in shape_t:
                    count *= d
            self._shapes.append((shape_t, shape_s, count))
        
    @testmethod
    def contructor(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            self.assertEqual(shape_ft, shape_fs)

    @testmethod
    def count(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            self.assertEqual(shape_ft.count(), shape_fs.count())
            self.assertEqual(shape_ft.count(), count)

    @testmethod
    def rank(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            self.assertEqual(len(shape_fs), len(shape_t))
            self.assertEqual(len(shape_ft), len(shape_t))
            self.assertEqual(shape_fs.rank(), len(shape_t))
            self.assertEqual(shape_ft.rank(), len(shape_t))

    @testmethod
    def shape(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            self.assertEqual(shape_fs.shape(), shape_t)
            self.assertEqual(shape_ft.shape(), shape_t)

    @testmethod
    def getitem(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            for index, d in enumerate(shape_t):
                self.assertEqual(shape_ft[index], d)
                self.assertEqual(shape_fs[index], d)

    @testmethod
    def iter(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            for d, dt, ds in zip(shape_t, shape_ft, shape_fs):
                self.assertEqual(dt, d)
                self.assertEqual(ds, d)

    @testmethod
    def str(self):
        for shape_t, shape_s, count in self._shapes:
            shape_ft = Shape(shape_t)
            shape_fs = Shape(shape_s)
            self.assertEqual(str(shape_fs), shape_s)
            self.assertEqual(str(shape_ft), shape_s)

