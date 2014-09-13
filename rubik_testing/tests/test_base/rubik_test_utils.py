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
           'RubikTestUtils',
          ]

import collections

from rubik import utils
from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestUtils(RubikTestCase):
    METHOD_NAMES = []

    def impl_flatten_sequence(self, sequence_class, depth, cmp_sequence):
        sequence = sequence_class([
            0,
            1,
            sequence_class([
                2,
                sequence_class([
                    3,
                    4,
                ]),
            ]),
            sequence_class([
                5,
                6,
            ]),
        ])
        flattener = getattr(utils, 'flatten_{}'.format(sequence_class.__name__))
        flattened_sequence = flattener(sequence, depth=depth)
        self.assertEqual(flattened_sequence, cmp_sequence)
        

    @testmethod
    def flatten_list_depth0(self):
        self.impl_flatten_sequence(list, 0, [0, 1, [2, [3, 4]], [5, 6]])

    @testmethod
    def flatten_list_depth1(self):
        self.impl_flatten_sequence(list, 1, [0, 1, 2, [3, 4], 5, 6])

    @testmethod
    def flatten_list_depth2(self):
        self.impl_flatten_sequence(list, 2, [0, 1, 2, 3, 4, 5, 6])

    @testmethod
    def flatten_list(self):
        self.impl_flatten_sequence(list, -1, [0, 1, 2, 3, 4, 5, 6])

    @testmethod
    def flatten_tuple_depth0(self):
        self.impl_flatten_sequence(tuple, 0, (0, 1, (2, (3, 4)), (5, 6)))

    @testmethod
    def flatten_tuple_depth1(self):
        self.impl_flatten_sequence(tuple, 1, (0, 1, 2, (3, 4), 5, 6))

    @testmethod
    def flatten_tuple_depth2(self):
        self.impl_flatten_sequence(tuple, 2, (0, 1, 2, 3, 4, 5, 6))

    @testmethod
    def flatten_tuple(self):
        self.impl_flatten_sequence(tuple, -1, (0, 1, 2, 3, 4, 5, 6))
