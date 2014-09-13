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
           'RubikTestTime',
          ]

import collections

from rubik.units import Time

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestTime(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestTime, self).setUp()
        self._times = collections.OrderedDict((
            (13,	(13,			'13s')),
            (90,	(90,			'1.50m')),
            (180,	(180,			'3m')),
            ('3s',	(3,			'3s')),
            ('7m',	(7 * 60,		'7m')),
            ('150m',	(150 * 60,		'2.50h')),
            ('5h',	(5 * 60 * 60,		'5h')),
            ('3d',	(3 * 60 * 60 * 24,	'3d')),
            ('21d',	(21 * 60 * 60 * 24,	'3w')),
            ('2w',	(2 * 60 * 60 * 24 * 7,  '2w')),
        ))
        
    @testmethod
    def constructor(self):
        for time_i, (time_s, time_hs) in self._times.iteritems():
            time = Time(time_i)
            time_h = Time(time_hs)
            self.assertEqual(time.get_seconds(), time_s)

    @testmethod
    def human(self):
        for time_i, (time_s, time_hs) in self._times.iteritems():
            time = Time(time_i)
            time_h = Time(time_hs)
            time_human = time.human()
            self.assertEqual(time_human, time_h)
            self.assertEqual(time_human.units(), time_h.units())
            self.assertEqual(str(time_human), time_hs)

    @testmethod
    def test_operations(self):
        time0 = Time("3600s")
        time1 = Time("1h")
        time2 = Time("59m")
        self.assertEqual(time0, time1)
        self.assertGreaterEqual(time0, time1)
        self.assertLessEqual(time0, time1)
        self.assertGreater(time0, time2)
        self.assertLess(time2, time0)
