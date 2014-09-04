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
           'RubikTestValues',
          ]

from ....values import Values

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestValues(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestValues, self).setUp()
        self._tuples = []
        for tpl in (), (1, ), (2, 4), (3, 5, 4, 6), (10, 30, 10, 40, 20, 33), ("alfa", "beta"), (0.3, 0.4, 0.5):
            self._tuples.append(tpl)
        
    @testmethod
    def values(self):
        for tpl in self._tuples:
            values = Values(tpl)
            self.assertEqual(values.values(), tpl)

    @testmethod
    def rank(self):
        for tpl in self._tuples:
            values = Values(tpl)
            self.assertEqual(len(values), len(tpl))
            self.assertEqual(values.rank(), len(tpl))

    @testmethod
    def getitem(self):
        for tpl in self._tuples:
            values = Values(tpl)
            for index, d in enumerate(tpl):
                self.assertEqual(values[index], d)

    @testmethod
    def iter(self):
        for tpl in self._tuples:
            values = Values(tpl)
            for vv, vt in zip(values, tpl):
                self.assertEqual(vv, vt)

    @testmethod
    def str(self):
        for tpl in self._tuples:
            values = Values(tpl)
            self.assertEqual(str(values), Values.__default_separator__.join(str(v) for v in tpl))

