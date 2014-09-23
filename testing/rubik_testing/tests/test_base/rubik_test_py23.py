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
           'RubikTestMemory',
          ]

import sys
import collections

from rubik import py23

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestPy23(RubikTestCase):
    METHOD_NAMES = []
        
    def setUp(self):
        super(RubikTestPy23, self).setUp()
        self.version = sys.version_info[0]

    @testmethod
    def py_2_or_3(self):
        if self.version == 2:
            self.assertFalse(py23.PY3)
        else:
            self.assertTrue(py23.PY3)

    @testmethod
    def lrange(self):
        l = list(range(2, 20, 3))
        self.assertEqual(l, py23.lrange(2, 20, 3))

    @testmethod
    def irange(self):
        l = list(range(2, 20, 3))
        self.assertEqual(l, list(py23.irange(2, 20, 3)))

    @testmethod
    def BASE_STRING(self):
        if self.version == 2:
            self.assertEqual(py23.BASE_STRING, basestring)
        else:
            self.assertEqual(py23.BASE_STRING, str)

    @testmethod
    def iteritems(self):
        d = {'a': 1, 'b': 2, 'c': 3}
        s = 0
        for k, v in py23.iteritems(d):
            s += v
        self.assertEqual(s, 6)
