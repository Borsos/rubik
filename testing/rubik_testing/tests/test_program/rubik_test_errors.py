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
           'RubikTestErrors',
          ]

from rubik.errors import *
from rubik.cubes import api as cb

from ...rubik_test_program import RubikTestProgram
from ...rubik_test_case import testmethod

class RubikTestErrors(RubikTestProgram):
    METHOD_NAMES = []

    @testmethod
    def error_RubikExpressionError(self):
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("AxB")'""",
            expect_failure=True,
        )
        self.assertNotEqual(returncode, 0)

    @testmethod
    def error_read_cube(self):
        returncode, output, error = self.run_program(
            """-e 'read_cube()'""",
            expect_failure=True,
        )
        self.assertNotEqual(returncode, 0)

    @testmethod
    def error_write_cube(self):
        returncode, output, error = self.run_program(
            """-e 'write_cube()'""",
            expect_failure=True,
        )
        self.assertNotEqual(returncode, 0)
