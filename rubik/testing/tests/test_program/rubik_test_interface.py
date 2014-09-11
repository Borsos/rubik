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
           'RubikTestInterface',
          ]


from ....conf import VERSION
from ....application import logo

from ...rubik_test_case import testmethod
from ...rubik_test_program import RubikTestProgram

class RubikTestInterface(RubikTestProgram):
    METHOD_NAMES = []

    @testmethod
    def help(self):
        returncode, output, error = self.run_program("--help")
        self.assertEqual(returncode, 0)

    @testmethod
    def usage(self):
        returncode, output, error = self.run_program("--usage")
        self.assertEqual(returncode, 0)

    @testmethod
    def logo(self):
        returncode, output, error = self.run_program("--logo")
        self.assertEqual(returncode, 0)
        self.assertEqual(output, "{}\n".format(logo.RUBIK))

    @testmethod
    def version(self):
        returncode, output, error = self.run_program("--version")
        self.assertEqual(returncode, 0)
        self.assertEqual(output, "rubik {}\n".format(VERSION))

    @testmethod
    def dry_run(self):
        returncode, output, error = self.run_program("-i non_existent.tmp1 -s 4x6 -o non_existent.tmp2 --dry-run")
        self.assertEqual(returncode, 0)

    @testmethod
    def report_dry_run(self):
        returncode, output, error = self.run_program("-i non_existent.tmp1 -s 4x6 -o non_existent.tmp2 --dry-run --report")
        self.assertEqual(returncode, 0)

    @testmethod
    def histogram(self):
        returncode, output, error = self.run_program("-e 'cb.random_cube((4, 5))' --histogram")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_expression(self):
        returncode, output, error = self.run_program("--help-expression")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_extractor(self):
        returncode, output, error = self.run_program("--help-extractor")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_user_defined_variables(self):
        returncode, output, error = self.run_program("--help-user-defined-variables")
        self.assertEqual(returncode, 0)

#    @testmethod
#    def help_numpy(self):
#        returncode, output, error = self.run_program("--help-numpy")
#        self.assertEqual(returncode, 0)
#
#    @testmethod
#    def help_cubes(self):
#        returncode, output, error = self.run_program("--help-cubes")
#        self.assertEqual(returncode, 0)

    @testmethod
    def help_filenames(self):
        returncode, output, error = self.run_program("--help-filenames")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_split(self):
        returncode, output, error = self.run_program("--help-split")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_environment_variables(self):
        returncode, output, error = self.run_program("--help-environment-variables")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_creating_cubes(self):
        returncode, output, error = self.run_program("--help-creating-cubes")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_output(self):
        returncode, output, error = self.run_program("--help-output")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_memory_usage(self):
        returncode, output, error = self.run_program("--help-memory-usage")
        self.assertEqual(returncode, 0)

#    @testmethod
#    def help_usage(self):
#        returncode, output, error = self.run_program("--help-usage")
#        self.assertEqual(returncode, 0)

