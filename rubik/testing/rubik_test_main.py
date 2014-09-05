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
           'RubikTestMain',
          ]

import collections
import fnmatch
import sys

from ..application.log import get_test_logger
from ..cubes.api import set_random_seed

from .rubik_test_runner import RubikTestRunner
from .rubik_test_suite import RubikTestSuite

from .tests import SUITES

from .rubik_test_conf import RUBIK_TEST_CONF


class RubikTestMain(object):
    def __init__(self, logger=None, verbose_level=0, trace_errors=False, patterns=None):
        if logger is None: 
            logger = conf.get_test_logger()
        self.logger = logger
        RUBIK_TEST_CONF.verbose_level = verbose_level
        RUBIK_TEST_CONF.trace_errors = trace_errors
        RUBIK_TEST_CONF.logger = logger

        self.name = self.__class__.__name__

        # global setup
        set_random_seed(100)
    
        # create runner
        self.rubik_test_runner = RubikTestRunner()

    def create_main_suite(self, patterns=None):
        # create suite
        main_suite = RubikTestSuite('Main')

        # add suites
        for suite_name, suite in SUITES.iteritems():
            suite_num_tests = 0
            for test_class, test_name in suite.test_classes_and_names():
                if self.match_patterns(test_name, patterns):
                    suite.addTest(test_class(test_name=test_name))
                    suite_num_tests += 1
            if suite_num_tests > 0:
                main_suite.addTest(suite)

        return main_suite
        
    def run(self, patterns):
        # create main suite
        main_suite = self.create_main_suite(patterns)

        # run tests
        self.result = self.rubik_test_runner.run(main_suite)
        return self.result
    
    @classmethod
    def match_patterns(cls, test_name, patterns):
        if patterns:
            for pattern in patterns:
                if fnmatch.fnmatchcase(test_name, pattern):
                    return True
            else:
                return False
        else:
            # select all
            return True

    @classmethod
    def filter_test_names(cls, patterns):
        for suite_name, suite in SUITES.iteritems():
            for test_name in suite.test_names():
                if cls.match_patterns(test_name, patterns):
                    yield test_name

