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

import collections

from ... import conf

class BaseVisualizerImpl(object):
    ATTRIBUTES = collections.OrderedDict()
    DIMENSIONS = "3D"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) == 3)
    DESCRIPTION = None
    def __init__(self, logger):
        self.logger = logger
        self.attributes = {}
        self.set_defaults()

    def set_defaults(self):
        for attribute_name, attribute in self.ATTRIBUTES.iteritems():
            self.attributes[attribute_name] = attribute.default()
            

    @classmethod
    def window_title(cls, name=None):
        if name is None:
            name = cls.__name__
        return "Rubik {} {}".format(name, conf.VERSION)

    def set_attributes(self, **attributes):
        for attribute_name, attribute_value in attributes.iteritems():
            attribute = self.ATTRIBUTES.get(attribute_name, None)
            if attribute is None:
                self.logger.warn("warning: invalid attribute {!r} ignored".format(attribute_name))
                #raise KeyError("invalid attribute {!r}".format(attribute_name))
            else:
                self.logger.info("setting attribute {}={!r}".format(attribute_name, attribute_value))
                self.attributes[attribute_name] = attribute.validate(attribute_name, attribute_value)
