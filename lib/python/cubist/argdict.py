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
    __re_label_split__ = re.compile("^([a-zA-Z]+\w*)\=(.*)")
    __formatter__ = "o{ordinal}"
    def __init__(self, factory, formatter=None, default=None):
        OrderedDict.__init__(self)
        self._default = default
        self._factory = factory
        if formatter is None:
            formatter = self.__formatter__
        self._formatter = formatter
        self._automatic_labels = {}
        self._ordinals = {}

    def add(self, value):
        label, value = self.label_split(value)
        value = self._factory(value)
        ordinal = len(self)
        if label is None:
            self._default = value
            label = self._formatter.format(ordinal=ordinal)
            self._automatic_labels[ordinal] = label
        self[label] = value
        self._ordinals[label] = ordinal
        return self
        
    def get_ordinal(self, label):
        return self._ordinals.get(label, None)

    def get(self, label, ordinal=None):
        if label in self:
            return self[label]
        else:
            automatic_label = self._automatic_labels.get(ordinal, None)
            if automatic_label in self:
                return self[automatic_label]
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
    def label_split(cls, value):
        m = cls.__re_label_split__.match(value)
        if m:
            label, value = m.groups()
        else:
            label = None
        return label, value

class InputArgDict(ArgDict):
    __formatter__ = 'i{ordinal}'

class OutputArgDict(ArgDict):
    __formatter__ = 'o{ordinal}'
