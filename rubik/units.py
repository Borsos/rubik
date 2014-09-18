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
import collections
import itertools

from .py23 import BASE_STRING

__all__ = [
              'Units',
              'Memory',
              'Time',
              'Bandwidth',
          ]
class UnitsError(Exception):
    pass

class Units(object):
    __re_split_string__ = re.compile(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(.*)$")
    def __init__(self, init, units=None):
        if isinstance(init, self.__class__):
            current_value, current_units = init._value, init._units
        elif isinstance(init, (int, float)):
            current_value = init
            current_units = None
        elif isinstance(init, BASE_STRING):
            try:
                current_value, current_units = self.from_string(init)
            except Exception as err:
                raise UnitsError("cannot make a {0} from {1!r}: {2}: {3}".format(self.__class__.__name__, init, err.__class__.__name__, err))
        else:
            raise UnitsError("cannot make a {0} from {1!r} of type {2}".format(self.__class__.__name__, init, type(init).__name__))
        if units is None:
            if current_units is not None:
                units = current_units
            else:
                units = self.__default_units__
        if not self.is_valid_unit(units):
            raise UnitsError("cannot make a {0} from {1!r}: invalid units {2!r}".format(self.__class__.__name__, init, units))
     
        if current_units is None:
            current_units = units
        else:
            if not self.is_valid_unit(current_units):
                raise UnitsError("cannot make a {0} from {1!r}: invalid units {2}".format(self.__class__.__name__, init, current_units))

        value = self.convert_units(current_value, current_units, units)
        self._units = units
        self._value = value

    @classmethod
    def from_string(cls, s):
        m = cls.__re_split_string__.match(s)
        if not m:
            raise UnitsError("cannot make a {0} from {1!r}".format(cls.__name__, s))
        v_s, u_s = m.groups()
        if not u_s:
            u_s = cls.__default_units__
        if u_s is None:
            raise UnitsError("cannot make a {0} from {1!r}: missing units".format(cls.__name__, s))
        return cls.value_from_string(v_s), cls.units_from_string(u_s)
        
    @classmethod
    def get_available_units(cls):
        raise NotImplementedError("Units.get_available_units()")
        
    @classmethod
    def get_units_factor(cls, units):
        raise NotImplementedError("Units.get_units_factor(...)")

    @classmethod
    def is_valid_unit(cls, u_s):
        raise NotImplementedError("Units.is_valid_unit(...)")

    @classmethod
    def convert_units(cls, value, from_units, to_units):
        if not cls.is_valid_unit(from_units):
            raise UnitsError("{}: invalid units {}".format(cls.__name__, from_units))
        if not cls.is_valid_unit(to_units):
            raise UnitsError("{}: invalid units {}".format(cls.__name__, to_units))
        if from_units == to_units:
            return value
        else:
            return cls.convert_value((float(value) * cls.get_units_factor(from_units)) / cls.get_units_factor(to_units))

    @classmethod
    def convert_value(cls, fv):
        iv = int(fv)
        if iv == fv:
            return iv
        else:
            return fv

    @classmethod
    def value_from_string(cls, v_s):
        try:
            fv = float(v_s)
        except:
            raise UnitsError("cannot make a float from {0}".format(v_s))
        return cls.convert_value(fv)

    def change_units(self, new_units):
        self._value = self.convert_units(self._value, self._units, new_units)
        self._units = new_units

    def get_value(self, to_units=None):
        if to_units is None:
            return self._value
        else:
            return self.convert_units(self._value, self._units, to_units)

    def convert(self, to_units):
        return self.__class__(self.convert_units(self.get_value(), self._units, to_units), units=to_units)
        
    @classmethod
    def units_from_string(cls, u_s):
        return u_s

    def value(self):
        return self._value

    def units(self):
        return self._units

    def __str__(self):
        return "{0}{1}".format(self._value, self._units)

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, str(self))

    def __nonzero__(self):
        return bool(self._value)
    __bool__ = __nonzero__

    @classmethod
    def _coerce(cls, other):
        if isinstance(other, cls):
            return other
        else:
            return cls(other)

    def _compare(self, other, comparison_operator):
        other = self._coerce(other)
        return comparison_operator(self._value, other.get_value(self._units))

    def __eq__(self, other):
        return self._compare(other, lambda x, y: x == y)

    def __ne__(self, other):
        return self._compare(other, lambda x, y: x != y)

    def __lt__(self, other):
        return self._compare(other, lambda x, y: x <  y)

    def __le__(self, other):
        return self._compare(other, lambda x, y: x <= y)

    def __gt__(self, other):
        return self._compare(other, lambda x, y: x >  y)

    def __ge__(self, other):
        return self._compare(other, lambda x, y: x >= y)

class SimpleUnits(Units):
    __units__ = collections.OrderedDict()
    __default_units__ = None
    __str_float_format__ = "{value:.2f}{units:s}"
    __str_int_format__ = "{value:d}{units:s}"

    @classmethod
    def get_available_units(cls):
        return cls.__units__.keys()

    @classmethod
    def get_units_factor(cls, units):
        return cls.__units__[units]

    @classmethod
    def is_valid_unit(cls, units):
        return units in cls.__units__

    @classmethod
    def units_from_string(cls, u_s):
        return u_s.lower()

    def base_value(self):
        return self.__units__[self._units] * self._value

    def human(self):
        base_value = self.base_value()
        diffs = []
        for units_s, units_v in self.__units__.items():
            diffs.append((units_s, abs(units_v - base_value)))
        diffs.sort(key=lambda x: x[-1])
        units = diffs[0][0]
        return self.convert(units)

    def __str__(self):
        v = self.convert_value(self._value)
        if isinstance(v, int):
            fmt = self.__str_int_format__
        else:
            fmt = self.__str_float_format__
        return fmt.format(value=self._value, units=self._units)

class Memory(SimpleUnits):
    __units__ = collections.OrderedDict((
        ('b',	 1),
        ('k',	 1024),
        ('kb',	 1024),
        ('m',	 1024 ** 2),
        ('mb',	 1024 ** 2),
        ('g',	 1024 ** 3),
        ('gb',	 1024 ** 3),
        ('t',	 1024 ** 4),
        ('tb',	 1024 ** 4),
        ('p',	 1024 ** 5),
        ('pb',	 1024 ** 5),
    ))
    __default_units__ = 'b'

    def get_bytes(self):
        return int(self.get_value('b'))


class Time(SimpleUnits):
    __units__ = collections.OrderedDict((
        ('s',	1),
        ('m',	60),
        ('h',	3600),
        ('d',	86400),
        ('w',	7 * 86400),
    ))
    __default_units__ = 's'

    def get_seconds(self):
        return self.get_value('s')

class AggregateUnits(Units):
    CACHE = {}

    @classmethod
    def _get_cache(cls, units):
        cache = cls.CACHE.setdefault(cls, {})
        if not units in cache:
            cache[units] = cls.split_units(units)
        return cache[units]

    @classmethod
    def _split_units(cls, units):
        raise NotImplementedError("AggregateUnits.split_units(...)")

class Bandwidth(AggregateUnits):
    @classmethod
    def get_available_units(cls):
        for _uml, _usl in itertools.product(Memory.get_available_units(), Time.get_available_units()):
            yield "{}/{}".format(_uml, _usl)

    @classmethod
    def split_units(cls, units):
        l = units.split('/', 1)
        if len(l) != 2:
            raise UnitsError("{}: invalid units {}".format(cls.__name__, units))
        um, ut = l
        if not Memory.is_valid_unit(um):
            raise UnitsError("{}: invalid units {}: invalid {} units {}".format(cls.__name__, units, Memory.__name__, um))
        if not Time.is_valid_unit(ut):
            raise UnitsError("{}: invalid units {}: invalid {} units {}".format(cls.__name__, units, Time.__name__, ut))
        un = '{}/{}'.format(um, ut) 
        uf = Memory.get_units_factor(um) / Time.get_units_factor(ut)
        return un, uf
        
    @classmethod
    def is_valid_unit(cls, units):
        try:
            un, uf = cls._get_cache(units)
            return True
        except:
            return False

    @classmethod
    def get_units_factor(cls, units):
        un, uf = cls._get_cache(units)
        return uf
