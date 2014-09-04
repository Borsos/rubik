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

import collections

from ....extractor import Extractor
from ....shape import Shape

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestExtractor(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestExtractor, self).setUp()
        shape_20x30x40 = Shape("20x30x40")
        shape_30x40x20 = Shape("30x40x20")
        shape_40x20x30 = Shape("40x20x30")
        self._exs = collections.OrderedDict((
            ('5:,:10,::5',	(shape_20x30x40, 24000, 15 * 10 * 8)),
            ('5:,:10,::5',	(shape_30x40x20, 24000, 25 * 10 * 4)),
            ('5:,:10,::5',	(shape_40x20x30, 24000, 35 * 10 * 6)),
        ))
        
    @testmethod
    def constructor(self):
        for ex_i, (shape, count, sub_count) in self._exs.iteritems():
            ex = Extractor(ex_i)
            ex_count, ex_sub_count = ex.get_counts(shape)
            self.assertEqual(ex_count, count)
            self.assertEqual(ex_sub_count, sub_count)

