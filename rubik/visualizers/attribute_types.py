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
    'IntegerAttributeType',
    'PositiveIntegerAttributeType',
    'FloatAttributeType',
    'FractionAttributeType',
    'BooleanAttributeType',
    'EnumAttributeType',
    'Attribute',
]

from .attribute_type import AttributeType

class AttributeType(object):
    PY_TYPE = None
    def __init__(self):
        self.name = self.__class__.__name__
        if isinstance(self.__class__.PY_TYPE, (list, tuple)):
            self.py_types = self.__class__.PY_TYPE
        else:
            self.py_types = (self.__class__.PY_TYPE, )
        self.py_type = self.py_types[0]

    def __str__(self):
        return "{}".format(self.__class__.__name__)

    def validate(self, name, value):
        return self.check(name, self.convert(name, value))

    def convert(self, name, value):
        if not isinstance(value, self.py_types):
            if isinstance(value, basestring):
                value = self.convert_string(name, value)
            else:
                raise ValueError("invalid value {v!r} of type {vt} for attribute {n}: cannot convert to {pt}".format(
                    v=value,
                    vt=type(value).__name__,
                    n=name,
                    pt=self.py_type.__name__))
        return value

    def convert_string(self, name, value):
        try:
            value = self.py_type(value)
        except ValueError:
            raise ValueError("invalid value {v!r} of type {vt} for attribute {n}: cannot convert to {pt}".format(
                v=value,
                vt=type(value).__name__,
                n=name,
                pt=self.py_type.__name__))
        return value

    def check(self, name, value):
        if not isinstance(value, self.py_types):
            raise ValueError("invalid value {v!r} of type {vt} for attribute {n}: not a {tl}".format(
                v=value,
                vt= type(value).__name__,
                n= name,
                tl='|'.join(pt.__name__ for pt in self.py_types)))
        return value

class IntegerAttributeType(AttributeType):
    PY_TYPE = int

class PositiveIntegerAttributeType(IntegerAttributeType):
    def check(self, name, value):
        super(PositiveIntegerAttributeType, self).check(name, value)
        if value <= 0:
            raise ValueError("invalid value {v!r} for attribute {n}: not a positive integer".format(v=value, n=name))
        return value


class FloatAttributeType(AttributeType):
    PY_TYPE = (float, int)
    pass

class FractionAttributeType(FloatAttributeType):
    def check(self, name, value):
        if not (0.0 <= value <= 1.0):
            raise ValueError("invalid value {v!r} for attribute {n}: not in range [0.0, 1.0]".format(v=value, n=name))
        return value
            
class BooleanAttributeType(AttributeType):
    PY_TYPE = bool
    def convert_string(self, name, value):
        if value.title() == "False":
            value = False
        elif value.title() == "True":
            value = True
        else:
            raise ValueError("invalid value {v!r} of type {vt} for attribute {n}: cannot convert to {pt}".format(
                v=value,
                vt=type(value).__name__,
                n=name,
                pt=self.py_type.__name__))
        return value


class EnumAttributeType(AttributeType):
    def __init__(self, values):
        self.values = values

    def validate(self, name, value):
        if not value in self.values:
            raise ValueError("invalid value {v!r} of type {vt} for attribute {n}: not a valid enumeration entry: {el}".format(
                v=value,
                vt=type(value).__name__,
                n=name,
                el='|'.join(repr(v) for v in self.values)))
        return value

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(repr(v) for v in self.values))

    def index(self, v):
        return self.values.index(v)

class Attribute(object):
    def __init__(self, description, attribute_type, default=None):
        self._description = description
        self._attribute_type = attribute_type
        self._default = default

    def attribute_type(self):
        return self._attribute_type

    def validate(self, name, value):
        return self._attribute_type.validate(name, value)

    def check(self, name, value):
        return value

    def description(self):
        return self._description

    def default(self):
        return self._default
