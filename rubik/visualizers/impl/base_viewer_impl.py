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
    'BaseViewerImpl',
]

import collections

from .base_class_impl import BaseClassImpl
from ... import conf

class BaseViewerImpl(BaseClassImpl):
    def __init__(self, controller, logger=None):
        if logger is None:
            logger = controller.logger
        super(BaseViewerImpl, self).__init__(logger=logger)
        self.controller = controller


    def feedback_attribute(self, attribute_name):
        setattr(self.controller, attribute_name, getattr(self, attribute_name))

