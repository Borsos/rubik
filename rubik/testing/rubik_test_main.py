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

from ..application.log import get_logger
from ..cubes.api import set_random_seed

from .rubik_test_runner import RubikTestRunner
from .rubik_test_suite import RubikTestSuite

from .tests import SUITES

from .rubik_test_conf import RUBIK_TEST_CONF


class RubikTestMain(object):
    def __init__(self, logger=None, verbose_level=0, trace_errors=False, patterns=None):
        if logger is None: 
            logger = conf.get_logger()
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
        suite_patterns = self.filter_suites(patterns)
        for suite_name, test_patterns in suite_patterns.iteritems():
            suite = SUITES[suite_name]
            suite.add_tests(test_patterns, self.logger)
            #self.logger.info("{}: adding suite {}".format(self.name, suite.suite_name))
            main_suite.addTest(suite)

        return main_suite
        
    def run(self, patterns):
        # create main suite
        main_suite = self.create_main_suite(patterns)

        # run tests
        self.result = self.rubik_test_runner.run(main_suite)
        return self.result
    
    @classmethod
    def split_pattern(cls, pattern):
        suite_pattern = '*'
        test_pattern = '*' 
        l = pattern.split('.', 2)
        if len(l) == 1:
            suite_pattern = l[0]
        else:
            suite_pattern, test_pattern = l
        return suite_pattern, test_pattern

    @classmethod
    def split_patterns(cls, patterns):
        if not patterns:
            return (('*', '*'), )
        else:
            return tuple(cls.split_pattern(pattern) for pattern in patterns)

    def filter_suites(self, patterns=None):
        # split patterns
        patterns = self.split_patterns(patterns)
        
        # filter suites
        suite_patterns = collections.OrderedDict()
        for suite_name, suite in SUITES.iteritems():
            for suite_pattern, test_pattern in patterns:
                if fnmatch.fnmatchcase(suite_name, suite_pattern):
                    suite_patterns.setdefault(suite_name, []).append(test_pattern)

        return suite_patterns

    def filter_test_names(self, patterns=None):
        suite_patterns = self.filter_suites(patterns)

        for suite_name, test_patterns in suite_patterns.iteritems():
            suite = SUITES[suite_name]
            for test_class, test_name in suite.filter_test_classes_and_names(test_patterns):
                yield "{}.{}".format(suite.suite_name, test_name)
