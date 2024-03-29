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
           'RubikTestProgram',
          ]

import shlex
import subprocess

from rubik.application.main import main
from rubik.application import log
from rubik import conf
from rubik.py23 import StringIO, BASE_STRING

from .rubik_test_case import RubikTestCase
from .rubik_test_conf import RUBIK_TEST_CONF

class RubikTestProgramBase(RubikTestCase):
    DEFAULT_PROGRAM_NAME = conf.PROGRAM_NAME
    DEFAULT_PREFIX_OPTIONS = '--random-seed 100'
    DEFAULT_SUFFIX_OPTIONS = ''

    def __init__(self, test_name, program_name=None):
        if program_name is None:
            program_name = self.DEFAULT_PROGRAM_NAME
        self.set_program_name(self.DEFAULT_PROGRAM_NAME)
        self.set_prefix_options(self.DEFAULT_PREFIX_OPTIONS)
        self.set_suffix_options(self.DEFAULT_SUFFIX_OPTIONS)
        super(RubikTestProgramBase, self).__init__(test_name=test_name)

    def setUp(self):
        super(RubikTestProgramBase, self).setUp()
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
        if isinstance(options, BASE_STRING):
            options = shlex.split(options)
        elif isinstance(options, (list, tuple, set, frozenset)):
            pass
        else:
            raise TypeError("invalid options object {!r} of type {}".format(options, type(options).__name__))
        if not isinstance(options, tuple):
            options = tuple(options)
        return options

    def get_options(self, options):
        if isinstance(options, BASE_STRING):
            options = tuple(shlex.split(options))
        return self.prefix_options + \
               options + \
               self.suffix_options

    def check_returncode(self, command_line, returncode, output, error, expect_failure):
        command = ' '.join([command_line[0]] + [repr(arg) for arg in command_line[1:]])
        assert_message = ""
        if expect_failure and returncode == 0:
            assert_message = "command {} did not fail as expected".format(command)
        elif (not expect_failure) and returncode != 0:
            assert_message = "command {} failed".format(command)
        if assert_message:
            self.logger.error(assert_message)
            self.logger.error("returncode is {}".format(returncode))
            if output is not None:
                self.logger.error("output is: <<<\n{}>>>".format(output))
            if error is not None:
                self.logger.error("error is: <<<\n{}>>>".format(error))
            raise AssertionError(assert_message)
        else:
            self.logger.debug("command {} returned {}".format(command, returncode))
            if output is not None:
                self.logger.debug("output is: <<<\n{}>>>".format(output))
            if error is not None:
                self.logger.debug("error is: <<<\n{}>>>".format(error))
            

    def run_program(self, options, join_stderr_stdout=True, expect_failure=False):
        options = self.get_options(options)
        command_line = (self.program_name, ) + options
        returncode, output, error = self.impl_run_program(
            command_line,
            join_stderr_stdout=join_stderr_stdout)
        command = ' '.join([command_line[0]] + [repr(a) for a in command_line[1:]])
        self.check_returncode(
            command_line=command_line,
            returncode=returncode,
            output=output,
            error=error,
            expect_failure=expect_failure,
        )
        return returncode, output, error

class RubikTestProgramCallMain(RubikTestProgramBase):
    def impl_run_program(self, command_line, join_stderr_stdout=True):
        options = command_line[1:]
        stdout = StringIO()
        if join_stderr_stdout:
            stderr = stdout
        else:
            stderr = StringIO()
        with log.swap_streams(stdout=stdout, stderr=stderr):
            try:
                returncode = main(options)
            except SystemExit as err:
                returncode = err.code
        output = stdout.getvalue()
        error = stderr.getvalue()
        return returncode, output, error
        
class RubikTestProgramSubprocess(RubikTestProgramBase):
    def impl_run_program(self, command_line, join_stderr_stdout=True):
        stdout = subprocess.PIPE
        if join_stderr_stdout:
            stderr = subprocess.STDOUT
        else:
            stderr = subprocess.PIPE
        p = subprocess.Popen(command_line, shell=False, stdout=stdout, stderr=stderr)
        output, error = p.communicate()
        returncode = p.returncode
        return returncode, output, error

RubikTestProgram = RubikTestProgramCallMain
