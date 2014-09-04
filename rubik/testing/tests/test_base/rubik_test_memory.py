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

from ....units import Memory

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestMemory(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestMemory, self).setUp()
        self._mems = collections.OrderedDict((
            (73,	(73,				'73b')),
            (1024,	(1024,				'1k')),
            (2048,	(2048,				'2k')),
            ('3b',	(3,				'3b')),
            ('7k',	(7 * 1024,			'7k')),
            ('7kb',	(7 * 1024,			'7k')),
            ('2560k',	(2560 * 1024,			'2.50m')),
            ('5m',	(5 * 1024 * 1024,		'5m')),
            ('5mb',	(5 * 1024 * 1024,		'5m')),
            ('2560mb',	(2560 * 1024 * 1024,		'2.50g')),
            ('3072mb',	(3072 * 1024 * 1024,		'3g')),
            ('13g',	(13 * 1024 * 1024 * 1024,	'13g')),
            ('13gb',	(13 * 1024 * 1024 * 1024,	'13g')),
        ))
        
    @testmethod
    def constructor(self):
        for mem_i, (mem_b, mem_hs) in self._mems.iteritems():
            mem = Memory(mem_i)
            self.assertEqual(mem.get_bytes(), mem_b)

    @testmethod
    def human(self):
        for mem_i, (mem_b, mem_hs) in self._mems.iteritems():
            mem = Memory(mem_i)
            mem_h = Memory(mem_hs)
            mem_human = mem.human()
            self.assertEqual(mem_human, mem_h)
            self.assertEqual(mem_human.units(), mem_h.units())
            self.assertEqual(str(mem_human), mem_hs)

