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
           'SUITE_CUBES',
          ]

from ...rubik_test_suite import RubikTestSuite

SUITE_CUBES = RubikTestSuite('Cubes')

from .rubik_test_input_output import RubikTestInputOutput
SUITE_CUBES.register_test_class(RubikTestInputOutput)

from .rubik_test_stats import RubikTestStats
SUITE_CUBES.register_test_class(RubikTestStats)

from .rubik_test_dtypes import RubikTestDtypes
SUITE_CUBES.register_test_class(RubikTestDtypes)

from .rubik_test_diff import RubikTestDiff
SUITE_CUBES.register_test_class(RubikTestDiff)

from .rubik_test_histogram import RubikTestHistogram
SUITE_CUBES.register_test_class(RubikTestHistogram)

from .rubik_test_creation import RubikTestCreation
SUITE_CUBES.register_test_class(RubikTestCreation)

from .rubik_test_comparison import RubikTestComparison
SUITE_CUBES.register_test_class(RubikTestComparison)
