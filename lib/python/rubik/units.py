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

from .errors import RubikUnitsError

class UnitsValue(object):
    __re_split_string__ = re.compile("^([\d]+)\s*(.*)$")
    __units__ = {}
    __default_units__ = None
    def __init__(self, init, default_units=None):
        if isinstance(init, self.__class__):
            value, units = init._value, init._units
        elif isinstance(init, (int, float)):
            value = init
            units = None
        elif isinstance(init, str):
            try:
                value, units = self.from_string(init)
            except Exception as err:
                raise RubikUnitsError("cannot make a {0} from {1!r}: {2}: {3}".format(self.__class__.__name__, init, err.__class__.__name__, err))
        else:
            raise RubikUnitsError("cannot make a {0} from {1!r} of type {2}".format(self.__class__.__name__, init, type(init).__name__))
        if default_units is None:
            if units is not None:
                default_units = units
            else:
                default_units = self.__default_units__
        assert default_units in self.__units__, "{0!r} is not a valid default_unis for {1}".format(default_units, self.__class__.__name__)
        self._units = default_units
        if units is None:
            units = self.default_units
        assert units in self.__units__, "{0!r} is not a valid unis for {1}".format(default_units, self.__class__.__name__)
        self._units = default_units
        self._value = self.convert_units(value, units, default_units)

    @classmethod
    def from_string(cls, s):
        m = cls.__re_split_string__.match(s)
        if not m:
            raise RubikUnitsError("cannot make a {0} from {1!r}".format(cls.__name__, s))
        v_s, u_s = m.groups()
        if not u_s:
            u_s = cls.__default_units__
        if u_s is None:
            raise RubikUnitsError("cannot make a {0} from {1!r}: missing units".format(cls.__name__, s))
        return cls.value_from_string(v_s), cls.units_from_string(u_s)
        
    @classmethod
    def value_from_string(cls, v_s):
        return int(v_s)

    @classmethod
    def units_from_string(cls, u_s):
        return u_s

    @classmethod
    def convert_units(cls, value, from_units, to_units):
        if from_units == to_units:
            return value
        else:
            return value * cls.__units__[from_units] / cls.__units__[to_units]

    def convert(self, to_units):
        return self.convert_units(self._value, self._units, to_units)

    def value(self):
        return self._value

    def units(self):
        return self._units

    def __str__(self):
        return "{0}{1}".format(self._value, self._units)

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, str(self))

class Memory(UnitsValue):
    __units__ = {
        'b': 1,
        'k': 1024,
        'kb': 1024,
        'm': 1024 ** 2,
        'mb': 1024 ** 2,
        'g': 1024 ** 3,
        'gb': 1024 ** 3,
        't': 1024 ** 4,
        'tb': 1024 ** 4,
        'p': 1024 ** 5,
        'pb': 1024 ** 5,
    }
    __default_units__ = 'b'

    def get_bytes(self):
        return self.convert('b')

    @classmethod
    def units_from_string(cls, u_s):
        return u_s.lower()
