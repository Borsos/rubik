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

from collections import OrderedDict

from .errors import CubistError

class ArgDict(OrderedDict):
    __re_name_split__ = re.compile("^([a-zA-Z]+\w*)\=(.*)")
    def __init__(self, factory, formatter="i{ordinal}", default=None):
        OrderedDict.__init__(self)
        self._default = default
        self._factory = factory
        self._formatter = formatter

    def add(self, value):
        name, value = self.name_split(value)
        value = self._factory(value)
        if name is None:
            self._default = value
            name = self._formatter.format(ordinal=len(self))
        self[name] = value
        return self
        
    def get(self, name):
        if name in self:
            return self[name]
        else:
            return self._default

    def store_function(self):
        def f_closure(self_, name):
            def f(x):
                return self_.add(x)
            for a in 'func_name', '__name__':
                setattr(f, a, name)
            return f
        return f_closure(self, self._factory.__name__)

    @classmethod
    def name_split(cls, value):
        m = cls.__re_name_split__.match(value)
        if m:
            name, value = m.groups()
        else:
            name = None
        return name, value

