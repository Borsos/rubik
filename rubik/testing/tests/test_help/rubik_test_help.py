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
           'RubikTestHelp',
          ]

from ....application import help_functions
from ....py23 import StringIO

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestHelp(RubikTestCase):
    METHOD_NAMES = []

    def impl_help(self, help_item):
        stream = StringIO()
        help_function = getattr(help_functions, 'help_{}'.format(help_item))
        help_function(test=True, interactive=False, writer=lambda x: stream.write(x))
        self.assertGreater(len(stream.getvalue()), 0)

    @testmethod
    def help_creating_cubes(self):
        self.impl_help('creating_cubes')

    @testmethod
    def help_dtypes(self):
        self.impl_help('dtypes')

    @testmethod
    def help_environment_variables(self):
        self.impl_help('environment_variables')

    @testmethod
    def help_expression(self):
        self.impl_help('expression')

    @testmethod
    def help_extractor(self):
        self.impl_help('extractor')

    @testmethod
    def help_user_defined_variables(self):
        self.impl_help('user_defined_variables')

    @testmethod
    def help_usage(self):
        self.impl_help('usage')

    @testmethod
    def help_split(self):
        self.impl_help('split')

    @testmethod
    def help_output(self):
        self.impl_help('output')

    @testmethod
    def help_memory_usage(self):
        self.impl_help('memory_usage')

    @testmethod
    def help_labeled_options(self):
        self.impl_help('labeled_options')

    @testmethod
    def help_filenames(self):
        self.impl_help('filenames')

