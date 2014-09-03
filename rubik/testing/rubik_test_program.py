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
           'RubikTestCase',
          ]

import shlex
import subprocess

from .rubik_test_case import RubikTestCase
from .rubik_test_conf import RUBIK_TEST_CONF

class RubikTestProgram(RubikTestCase):
    DEFAULT_PROGRAM_NAME = 'rubik'
    DEFAULT_PREFIX_OPTIONS = '--random-seed 100'
    DEFAULT_SUFFIX_OPTIONS = ''
    def __init__(self, test_name):
        self.set_program_name(self.DEFAULT_PROGRAM_NAME)
        self.set_prefix_options(self.DEFAULT_PREFIX_OPTIONS)
        self.set_suffix_options(self.DEFAULT_SUFFIX_OPTIONS)
        super(RubikTestProgram, self).__init__(test_name=test_name)

    def setUp(self):
        super(RubikTestProgram, self).setUp()
        self.prepend_prefix_options('--verbose-level={}'.format(RUBIK_TEST_CONF.verbose_level))
        if RUBIK_TEST_CONF.trace_errors:
            self.prepend_prefix_options('--trace-errors')
    
    def set_program_name(self, program_name):
        self.program_name = program_name

    def set_prefix_options(self, prefix_options):
        self.prefix_options = self.make_options(prefix_options)

    def append_prefix_options(self, prefix_options):
        self.prefix_options += self.make_options(prefix_options)

    def prepend_prefix_options(self, prefix_options):
        self.prefix_options = self.make_options(prefix_options) + self.prefix_options

    def set_suffix_options(self, suffix_options):
        self.suffix_options = self.make_options(suffix_options)

    def append_suffix_options(self, suffix_options):
        self.suffix_options += self.make_options(suffix_options)

    def prepend_suffix_options(self, suffix_options):
        self.suffix_options = self.make_options(suffix_options) + self.suffix_options

    @classmethod
    def make_options(cls, options):
        if options is None:
            options = ()
        if isinstance(options, str):
            options = shlex.split(options)
        elif isinstance(options, (list, tuple, set, frozenset)):
            pass
        else:
            raise TypeError("invalid options object {!r} of type {}".format(options, type(options).__name__))
        if not isinstance(options, tuple):
            options = tuple(options)
        return options

    def get_command_line(self, options):
        return (self.program_name, ) + \
               self.prefix_options + \
               self.make_options(options) + \
               self.suffix_options

    def check_returncode(self, command_line, returncode, output, error, expect_failure):
        command = ' '.join([command_line[0]] + [repr(a) for a in command_line[1:]])
        assert_message = ""
        if expect_failure and returncode == 0:
            assert_message = "command {} did not fail as expected".format(command)
        elif (not expect_failure) and returncode != 0:
            assert_message = "command {} failed".format(command)
        logger = RUBIK_TEST_CONF.logger
        if assert_message:
            logger.error(assert_message)
            logger.error("returncode is {}".format(returncode))
            if output is not None:
                logger.error("output is: <<<\n{}>>>".format(output))
            if error is not None:
                logger.error("error is: <<<\n{}>>>".format(error))
            raise AssertionError(assert_message)
        else:
            logger.debug("command {} returned {}".format(command, returncode))
            if output is not None:
                logger.debug("output is: <<<\n{}>>>".format(output))
            if error is not None:
                logger.debug("error is: <<<\n{}>>>".format(error))
            

    def run_program(self, options, stdout=None, stderr=None, expect_failure=False):
        command_line = self.get_command_line(options)
        if stdout is None:
            stdout = subprocess.PIPE
        if stderr is None:
            stderr = subprocess.STDOUT
        p = subprocess.Popen(command_line, shell=False, stdout=stdout, stderr=stderr)
        output, error = p.communicate()
        returncode = p.returncode
        self.check_returncode(
            command_line=command_line,
            returncode=returncode,
            output=output,
            error=error,
            expect_failure=expect_failure,
        )
        return returncode, output, error

