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
    'BaseClassImpl',
]

import weakref
from ... import conf

from traitsui.ui_info import UIInfo
class BaseClassImpl(object):
    WINDOW_TITLE = None
    CURRENT_ID = 0
    ID_FORMAT = "{id}"
    def __init__(self, logger):
        self.logger = logger
        self.name = self.reserve_id()
        self.handler_infos = []

    def add_handler_info(self, handler, info):
        self.handler_infos.append((weakref.ref(handler), weakref.ref(info)))

    @classmethod
    def reserve_id(cls):
        cur_id = cls.CURRENT_ID
        cls.CURRENT_ID += 1
        return cls.ID_FORMAT.format(id=cur_id)
            
    @classmethod
    def set_window_title(cls, title=None):
        if title is None:
            title = cls.ID_FORMAT.format(id=cls.CURRENT_ID)
        cls.WINDOW_TITLE = title

    @classmethod
    def consume_window_title(cls):
        title = cls.WINDOW_TITLE
        cls.WINDOW_TITLE = None
        return title

    @classmethod
    def default_window_title(cls):
        if cls.WINDOW_TITLE is None:
            cls.set_window_title()
        return cls.consume_window_title()

    def has_trait(self, trait):
        return trait in self.editable_traits()

    def log_trait_change(self, traits):
        self.logger.info("{}: changed traits: {}".format(self.name, traits))

    def close_uis(self, finish=True, close=True):
        self.logger.info("{}: closing windows".format(self.name))
        for handler_ref, info_ref in reversed(self.handler_infos):
            handler = handler_ref()
            info = info_ref()
            if info is not None and handler is not None:
                self.logger.info("{}: closing handler {}, info {}".format(self.name, handler, info))
                if finish and info.ui:
                    info.ui.finish()
                if close:
                    handler.close(info, True)
