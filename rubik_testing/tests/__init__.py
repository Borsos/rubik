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
            'SUITES',
          ]

import collections

class RubikTestSuites(collections.OrderedDict):
    def add_suite(self, suite):
        self[suite.suite_name] = suite

SUITES = RubikTestSuites()

from .test_base import SUITE_BASE
SUITES.add_suite(SUITE_BASE)

from .test_cubes import SUITE_CUBES
SUITES.add_suite(SUITE_CUBES)

from .test_help import SUITE_HELP
SUITES.add_suite(SUITE_HELP)

from .test_program import SUITE_PROGRAM
SUITES.add_suite(SUITE_PROGRAM)
