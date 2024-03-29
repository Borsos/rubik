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
           'SUITE_PROGRAM',
          ]

from ...rubik_test_suite import RubikTestSuite

SUITE_PROGRAM = RubikTestSuite('Program')

from .rubik_test_interface import RubikTestInterface
SUITE_PROGRAM.register_test_class(RubikTestInterface)

from .rubik_test_config import RubikTestConfig
SUITE_PROGRAM.register_test_class(RubikTestConfig)

from .rubik_test_opt import RubikTestOpt
SUITE_PROGRAM.register_test_class(RubikTestOpt)

from .rubik_test_work import RubikTestWork
SUITE_PROGRAM.register_test_class(RubikTestWork)

from .rubik_test_usage import RubikTestUsage
SUITE_PROGRAM.register_test_class(RubikTestUsage)

from .rubik_test_std import RubikTestStd
SUITE_PROGRAM.register_test_class(RubikTestStd)

from .rubik_test_info import RubikTestInfo
SUITE_PROGRAM.register_test_class(RubikTestInfo)

from .rubik_test_errors import RubikTestErrors
SUITE_PROGRAM.register_test_class(RubikTestErrors)
