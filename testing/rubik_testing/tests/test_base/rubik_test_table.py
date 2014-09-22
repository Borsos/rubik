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
           'RubikTestTable',
          ]

from rubik.table import table, Table

from ...rubik_test_case import RubikTestCase, testmethod


class RubikTestTable(RubikTestCase):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestTable, self).setUp()

    @testmethod
    def classTable(self):
        headers = ["", "KEY", "VALUE"]
        t = Table(headers=headers)
        t.add_row((10, "alpha", "Hello"))
        t.add_str_row((5, "beta", "World"))
        t.add_repr_row((200, "gamma", 3.5))
        text = t.render()
        cmp_text = """\
    KEY     VALUE
10  alpha   Hello
5   beta    World
200 'gamma' 3.5"""
        #print '-' * 80
        #print text
        #print '-' * 80
        #print cmp_text
        #print '-' * 80
        self.assertEqual(text, cmp_text)

    @testmethod
    def function_table(self):
        headers = ["", "KEY", "VALUE"]
        rows = []
        rows.append((10, "alpha", "Hello"))
        rows.append(str(i) for i in (5, "beta", "World"))
        rows.append(repr(i) for i in (200, "gamma", 3.5))
        text = table(rows, headers=headers)
        cmp_text = """\
    KEY     VALUE
10  alpha   Hello
5   beta    World
200 'gamma' 3.5"""
        #print '=' * 80
        #print text
        #print '=' * 80
        #print cmp_text
        #print '=' * 80
        self.assertEqual(text, cmp_text)
