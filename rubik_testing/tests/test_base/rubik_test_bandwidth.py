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
           'RubikTestBandwidth',
          ]

import collections

from rubik.units import Bandwidth

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestBandwidth(RubikTestCase):
    METHOD_NAMES = []

    @testmethod
    def constructor(self):
        bw0 = Bandwidth("2.5mb/s")
        bw1 = Bandwidth("25kb/s")
        self.assertGreater(bw0, bw1)
        self.assertNotEqual(bw0, bw1)

    @testmethod
    def test_is_valid_unit(self):
        self.assertTrue(Bandwidth.is_valid_unit("m/s"))
        self.assertFalse(Bandwidth.is_valid_unit("s/m"))
