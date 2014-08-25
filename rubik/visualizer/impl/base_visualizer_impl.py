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

from .base_class_impl import BaseClassImpl
from ... import conf


class BaseVisualizerImpl(BaseClassImpl):
    CURRENT_ID = 0
    ID_FORMAT = "View[{id}]"
    def __init__(self, controller, logger=None, title=None):
        if logger is None:
            logger = controller.logger
        super(BaseVisualizerImpl, self).__init__(logger=logger, title=title)
        self.feedback = True
        self.controller = controller

    def get_feedback(self):
        return self._feedback
    def set_feedback(self, feedback):
        self._feedback = bool(feedback)
    feedback = property(get_feedback, set_feedback)

    def feedback_attribute(self, attribute_name, attribute_value=None):
        if attribute_value is None:
            attribute_value = getattr(self, attribute_name)
        if self.feedback:
            self.logger.info("{}: sending feedback for attribute {}={!r} to controller {}".format(self.name, attribute_name, attribute_value, self.controller.name))
            setattr(self.controller, attribute_name, attribute_value)

