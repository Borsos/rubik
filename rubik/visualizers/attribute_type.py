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
    'AttributeType',
]

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

