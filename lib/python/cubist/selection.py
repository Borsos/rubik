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

import re

from .pick import Pick
from .values import Values

class Selection(Values):

    def rank(self):
        return len(self._values)

    def picks(self, origins=None):
        if origins is None:
            origins = Origins.from_rank(self.rank())
        return tuple(pick.value(origin) for pick, origin in zip(self._values, origins.values()))

    @classmethod
    def _item_from_string(cls, item):
        return Pick(item)
