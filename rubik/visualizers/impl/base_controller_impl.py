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
    'BaseControllerImpl',
]

import collections

from .base_class_impl import BaseClassImpl
from ... import conf

class BaseControllerImpl(BaseClassImpl):
    ATTRIBUTES = collections.OrderedDict()
    DIMENSIONS = "3D"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) == 3)
    DESCRIPTION = None
    def __init__(self, logger, attributes):
        super(BaseControllerImpl, self).__init__(logger)
        self.attributes = {}
        
        self.set_attributes(**attributes)

    def set_defaults(self):
        for attribute_name, attribute in self.ATTRIBUTES.iteritems():
            self.attributes[attribute_name] = attribute.default()
            
    def set_attributes(self, **attributes):
        for attribute_name, attribute_value in attributes.iteritems():
            if not attribute_name in self.ATTRIBUTES:
                self.logger.warn("warning: invalid attribute {!r} ignored".format(attribute_name))
        for attribute_name, attribute in self.ATTRIBUTES.iteritems():
            if attribute_name in attributes:
                attribute_value = attributes[attribute_name]
                self.logger.info("setting attribute {}={!r}".format(attribute_name, attribute_value))
                #print "{!r} {!r} {!r}".format(attribute_name, attribute_value, attribute)
                self.attributes[attribute_name] = attribute.validate(attribute_name, attribute_value)
            else:
                attribute_value = attribute.default()
                self.logger.info("setting attribute {} to default {!r}".format(attribute_name, attribute_value))
                self.attributes[attribute_name] = attribute_value
