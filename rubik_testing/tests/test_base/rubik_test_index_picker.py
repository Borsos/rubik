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

from rubik.index_picker import IndexPicker

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestIndexPicker(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestIndexPicker, self).setUp()
        self._ips = collections.OrderedDict((
            (4,			(4,				(4, 5, 1))),
            ('4',		(4,				(4, 5, 1))),
            (':',		(slice(None, None, None),	(0, 5, 1))),
            ('2:',		(slice(2, None, None),		(2, 5, 1))),
            (':9',		(slice(None, 9, None),		(0, 5, 1))),
            ('2:9',		(slice(2, 9, None),		(2, 5, 1))),
            ('::',		(slice(None, None, None),	(0, 5, 1))),
            ('2::',		(slice(2, None, None),		(2, 5, 1))),
            (':9:',		(slice(None, 9, None),		(0, 5, 1))),
            ('::3',		(slice(None, None, 3),		(0, 5, 3))),
            ('2:9:',		(slice(2, 9, None),		(2, 5, 1))),
            ('2::3',		(slice(2, None, 3),		(2, 5, 3))),
            (':9:3',		(slice(None, 9, 3),		(0, 5, 3))),
            ('2:9:3',		(slice(2, 9, 3),		(2, 5, 3))),
        ))
        
    @testmethod
    def constructor(self):
        for ip_i, (ip_v, ip_indices) in self._ips.items():
            ip = IndexPicker(ip_i)
            ip_value = ip.value()
            self.assertEqual(ip_value, ip_v)

    @testmethod
    def get_indices(self):
        for ip_i, (ip_v, ip_indices) in self._ips.items():
            ip = IndexPicker(ip_i)
            self.assertEqual(ip.get_indices(5), ip_indices)

    @testmethod
    def is_slice(self):
        for ip_i, (ip_v, ip_indices) in self._ips.items():
            ip = IndexPicker(ip_i)
            self.assertEqual(ip.is_slice(), isinstance(ip_v, slice))

