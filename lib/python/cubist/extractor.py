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

from .shape import Shape
from .errors import CubistError
from .values import Values
from .index_picker import IndexPicker

class Extractor(Values):
    __default_separator__ = ', '
    def rank(self):
        return len(self._values)

    def index_pickers(self):
        return tuple(index_picker.value() for index_picker in self._values)

    @classmethod
    def _item_from_string(cls, item):
        return IndexPicker(item)

    def get_counts(self, shape):
        if isinstance(shape, Shape):
            shape = shape.shape()
        if len(shape) != self.rank():
            raise CubistError("invalid shape {0} for extactor {1}: rank {2} != {3}".format(shape, self, len(shape), self.rank()))
        if self.rank() == 0:
            count = 0
            sub_count = 0
        else:
            count = 1
            sub_count = 1
            for index_picker, dim in zip(self._values, shape):
                count *= dim
                if index_picker.is_slice():
                    start, stop, step = index_picker.get_indices(dim)
                    sub_count *= (stop - start) / step
        return count, sub_count

    
