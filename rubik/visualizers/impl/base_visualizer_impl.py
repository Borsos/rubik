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
    'BaseVisualizerImpl',
]

class BaseVisualizerImpl(object):
    ATTRIBUTES = {}
    DIMENSIONS = [3]
    DESCRIPTION = None
    def __init__(self):
        self.attributes = {}
        self.set_defaults()

    def set_defaults(self):
        for attribute_name, attribute in self.ATTRIBUTES.iteritems():
            self.attributes[attribute_name] = attribute.default()
            

    def set_attributes(self, **attributes):
        for attribute_name, attribute_value in attributes.iteritems():
            attribute = self.ATTRIBUTES.get(attribute_name, None)
            if attribute is None:
                raise KeyError("invalid attribute {!r}".format(attribute_name))
            self.attributes[attribute_name] = attribute.validate(attribute_name, attribute_value)
