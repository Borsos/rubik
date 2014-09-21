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
import re
import sys

from rubik.cubes.api import set_random_seed

from .application.log import get_test_logger
from .rubik_test_runner import RubikTestRunner
from .rubik_test_suite import RubikTestSuite

from .tests import SUITES

from .rubik_test_conf import RUBIK_TEST_CONF


class RubikTestMain(object):
    RE_NEGATE = re.compile("^[\!\^]")
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
        suite_id_num_tests = collections.Counter()
        suite_by_id = {}
        for suite, test_class, test_name in self.filter_tests(patterns):
            suite.addTest(test_class(test_name=test_name))
            suite_id_num_tests[id(suite)] += 1
            suite_by_id[id(suite)] = suite
        for suite_id, num_tests in suite_id_num_tests.items():
            if num_tests > 0:
                main_suite.addTest(suite_by_id[suite_id])

        return main_suite
        
    def run(self, patterns):
        # create main suite
        main_suite = self.create_main_suite(patterns)

        # run tests
        self.result = self.rubik_test_runner.run(main_suite)
        return self.result
    
    @classmethod
    def filter_tests(cls, patterns):
        if not patterns:
            patterns = ['*']
        selected_tests = []
        for pattern in patterns:
            if pattern and pattern[0] in '!^':
                negate = True
                pattern = pattern[1:]
            else:
                negate = False
            if negate:
                l = []
                for suite, test_class, test_name in selected_tests:
                    if not fnmatch.fnmatchcase(test_name, pattern):
                        l.append(test_name)
                selected_tests = l
            else:
                for suite_name, suite in SUITES.items():
                    for test_class, test_name in suite.test_classes_and_names():
                        if fnmatch.fnmatchcase(test_name, pattern):
                            selected_tests.append((suite, test_class, test_name))
        return selected_tests

    @classmethod
    def filter_test_names(cls, patterns):
        for suite, test_class, test_name in cls.filter_tests(patterns):
            yield test_name
