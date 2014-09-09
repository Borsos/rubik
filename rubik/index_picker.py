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

from .py23 import BASE_STRING

class IndexPicker(object):
    def __init__(self, init):
        if isinstance(init, IndexPicker):
            self._value = init._value
        elif isinstance(init, (int, slice)):
            self._value = init
        elif isinstance(init, BASE_STRING):
            self._value = self._from_string(init)
        else:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=self.__class__.__name__,
                t=type(init).__name__,
                o=init))

    def value(self):
        return self._value

    @classmethod
    def _from_string(cls, value):
        if ':' in value:
            l = value.split(':', 2)
            start = cls._default_int(l[0], None)
            stop = cls._default_int(l[1], None)
            if len(l) == 2:
                step = None
            else:
                step = cls._default_int(l[2], None)
            return slice(start, stop, step)
        else:
            return cls._default_int(value, slice(None, None, None))
            
    @classmethod
    def _default_int(cls, value, default):
        value = value.strip()
        if value:
            return int(value)
        else:
            return default
            
    def __str__(self):
        if isinstance(self._value, slice):
            start = self._value.start
            stop = self._value.stop
            step = self._value.step
            l = []
            if start is None:
                l.append('')
            else:
                l.append(str(start))
            if stop is None:
                l.append('')
            else:
                l.append(str(stop))
            if step is not None:
                l.append(str(step))
            return ':'.join(l)
        else:
            return str(self._value)

    def get_indices(self, dim):
        if isinstance(self._value, slice):
            return self._value.indices(dim)
        else:
            if 0 <= self._value < dim:
                return self._value, self._value + 1, 1
            else:
                return self._value, self._value, 1

    def is_slice(self):
        return isinstance(self._value, slice)

    def __repr__(self):
        return repr(self._value)
