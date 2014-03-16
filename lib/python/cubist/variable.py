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

class VariableDefinition(object):
    __variables__ = {}
    def __init__(self, init):
        if isinstance(init, str):
            name, value = self._from_string(init)
        else:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=self.__class__.__name__,
                t=type(init).__name__,
                o=init))
        if name in self.__variables__:
            raise ValueError("invalid variable name {n}: already defined".format(
                n=name))
        self._name = name
        self._value = value
        self.__class__.register(self)

    @classmethod
    def register(cls, instance):
        cls.__variables__[instance._name] = instance

    def name(self):
        return self._name

    def value(self):
        return self._value

    @classmethod
    def _from_string(cls, value):
        l = value.split("=", 1)
        if len(l) == 1:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=cls.__name__,
                t=type(value).__name__,
                o=init))
        else:
            name, value = l
            return name, value

    def evaluate(self, globals_d=None, locals_d=None):
        if globals_d is None:
            globals_d = {}
        if locals_d is None:
            l_d = {}
        else:
            l_d = locals_d.copy()
        l_d.update(self.__variables__)
        try:
            value = eval(self._value, globals_d, l_d)
        except Exception as err:
            raise ValueError("variable {n}: cannot converto {s!r} to a valid python object: {et}: {e}".format(
                n=self._name,
                s=self._value,
                et=err.__class__.__name__,
                e=err))
        self._value = value
    def __str__(self):
        return "{0}={1!r}".format(self._name, self._value)

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, str(self))