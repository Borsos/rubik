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

import re

class Clip(object):
    def __init__(self, init):
        if isinstance(init, Clip):
            self._min = init._min
            self._max = init._max
        elif isinstance(init, (list, tuple)):
            self._min, self._max = init
        elif isinstance(init, str):
            self._min, self._max = self._from_string(init)
        else:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=self.__class__.__name__,
                t=type(init).__name__,
                o=init))

    def min(self):
        return self._min

    def max(self):
        return self._max

    @classmethod
    def _from_string(cls, value):
        l = value.split(':', 1)
        cmin = cls._default_float(l[0], None)
        if len(l) == 2:
            cmax = cls._default_float(l[1], None)
        else:
            cmax = None
        return cmin, cmax
            
    @classmethod
    def _default_float(cls, value, default):
        value = value.strip()
        if value:
            return float(value)
        else:
            return default
            
    def __str__(self):
        l = []
        if self._min is not None:
            l.append(str(self._min))
        if self._max is not None:
            l.append(str(self._max))
        return ':'.join(l)

    def __repr__(self):
        return "{0}(min={1!r}, max={2!r})".format(self.__class__.__name__, self._min, self._max)
