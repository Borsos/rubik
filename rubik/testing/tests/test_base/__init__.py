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
           'SUITE_BASE',
          ]

from ...rubik_test_suite import RubikTestSuite

SUITE_BASE = RubikTestSuite()

from .rubik_test_values import RubikTestValues
SUITE_BASE.add_test_class(RubikTestValues)

from .rubik_test_shape import RubikTestShape
SUITE_BASE.add_test_class(RubikTestShape)

from .rubik_test_memory import RubikTestMemory
SUITE_BASE.add_test_class(RubikTestMemory)

from .rubik_test_time import RubikTestTime
SUITE_BASE.add_test_class(RubikTestTime)

from .rubik_test_index_picker import RubikTestIndexPicker
SUITE_BASE.add_test_class(RubikTestIndexPicker)
