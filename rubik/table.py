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

from .py23 import irange

class Table(object):
    def __init__(self, headers=None):
        self.rows = []
        if headers:
            self.add_str_row(headers)

    def add_row(self, iterable):
        self.add_str_row(iterable)

    def add_converted_row(self, iterable, converter):
        self.rows.append(tuple(converter(i) for i in iterable))

    def add_str_row(self, iterable):
        self.add_converted_row(iterable, str)

    def add_repr_row(self, iterable):
        self.add_converted_row(iterable, repr)

    def render(self):
        num_columns = max(len(row) for row in self.rows)
        rows = []
        for row in self.rows:
            rows.append(row + tuple('' for i in irange(num_columns - len(row))))
        ln = [max(len(row[i]) for row in rows) for i in irange(num_columns)]
        f_list = []
        for lni in ln[:-1]:
            f_list.append("{{:{}s}}".format(lni))
        f_list.append("{}")
        fmt = ' '.join(f_list)
        return '\n'.join(fmt.format(*row) for row in rows)

def table(rows, headers=None):
    t = Table(headers=headers)
    for row in rows:
        t.add_row(row)
    return t.render()
