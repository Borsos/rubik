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
from .shape import Shape
from .values import Values

class Selection(Values):

    def rank(self):
        return len(self._values)

    def picks(self):
        return tuple(pick.value() for pick in self._values)

    @classmethod
    def _item_from_string(cls, item):
        return Pick(item)

    def get_counts(self, shape):
        if isinstance(shape, Shape):
            shape = shape.shape()
        assert len(shape) == self.rank()
        if self.rank() == 0:
            count = 0
            sub_count = 0
        else:
            count = 1
            sub_count = 1
            for pick, dim in zip(self._values, shape):
                count *= dim
                if isinstance(pick, slice):
                    start, stop, step = pick.indices(dim)
                    sub_count *= (stop - start) / step
        return count, sub_count
