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
           'SUITE_MAIN',
          ]

from ...rubik_test_suite import RubikTestSuite

SUITE_MAIN = RubikTestSuite()

from .rubik_test_execution import RubikTestExecution
SUITE_MAIN.add_test_class(RubikTestExecution)

from .rubik_test_work import RubikTestWork
SUITE_MAIN.add_test_class(RubikTestWork)

