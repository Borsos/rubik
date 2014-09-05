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
           'RubikTestExecution',
          ]


from ....conf import VERSION

from ...rubik_test_case import testmethod
from ...rubik_test_program import RubikTestProgram

class RubikTestExecution(RubikTestProgram):
    METHOD_NAMES = []

    @testmethod
    def help(self):
        return

        returncode, output, error = self.run_program("--help")
        self.assertEqual(returncode, 0)

    @testmethod
    def version(self):
        return

        try:
            returncode, output, error = self.run_program("--version")
        except SystemExit as err:
            returncode = 0
        self.assertEqual(returncode, 0)
        self.assertEqual(output, "rubik {}\n".format(VERSION))
