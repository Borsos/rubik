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
    'Attribute',
]

class Attribute(object):
    def __init__(self, description, attribute_type, default=None):
        self._description = description
        self._attribute_type = attribute_type
        self._default = default

    def attribute_type(self):
        return self._attribute_type

    def validate(self, name, value):
        #print self._attribute_type.__class__.__name__, repr(name), repr(value)
        return self._attribute_type.validate(name, value)

    def check(self, name, value):
        return value

    def description(self):
        return self._description

    def default(self):
        return self._default
