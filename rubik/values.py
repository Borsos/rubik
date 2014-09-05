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

import re

class Values(object):
    __re_split__ = re.compile("[,x]")
    __default_separator__ = 'x'
    def __init__(self, init):
        if isinstance(init, Values):
            values = init._values
        elif isinstance(init, (list, tuple)):
            values = init
        elif isinstance(init, str):
            values = self._from_string(init)
        elif hasattr(init, '__iter__'):
            values = init
        else:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=self.__class__.__name__,
                t=type(init).__name__,
                o=init))
        self._values = tuple(values)

    def values(self):
        return self._values

    def rank(self):
        return len(self._values)

    def split_first(self):
        return self._values[0], self.__class__(self._values[1:])

    def __iter__(self):
        return iter(self._values)

    @classmethod
    def _item_from_string(cls, value):
        return int(value)

    @classmethod
    def _from_string(cls, value):
        values = []
        for item in cls.__re_split__.split(value):
            if item:
                values.append(cls._item_from_string(item))
        return values
            
    def __len__(self):
        return len(self._values)

    def __str__(self):
        return str(self.__default_separator__.join(str(i) for i in self._values))

    def __repr__(self):
        return "{c}({s!r})".format(c=self.__class__.__name__, s=self._values)

    def __getitem__(self, index):
        return self._values[index]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._values == other._values
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self._values != other._values
        else:
            return False
       
