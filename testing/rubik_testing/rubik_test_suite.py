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
           'RubikTestSuite',
          ]

import unittest
import tempfile
import shutil
import fnmatch
import sys
import os

from rubik.application.tempdir import chtempdir

from .rubik_test_conf import RUBIK_TEST_CONF

class RubikTestSuite(unittest.TestSuite):
    def __init__(self, suite_name, *n_args, **p_args):
        super(RubikTestSuite, self).__init__(*n_args, **p_args)
        self._registered_test_classes = []
        self.suite_name = suite_name
        self._logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = RUBIK_TEST_CONF.logger
        return self._logger

    def run(self, result):
        with chtempdir(prefix="tmp.", dir=os.getcwd()) as temp_dir_info:
            num_prev_failures = len(result.failures)
            num_prev_errors = len(result.errors)
            super(RubikTestSuite, self).run(result)
            num_curr_failures = len(result.failures)
            num_curr_errors = len(result.errors)
            num_failures = num_curr_failures - num_prev_failures
            num_errors = num_curr_errors - num_prev_errors
            if num_failures > 0 or num_errors > 0:
                self.logger.error("suite {}: {} errors, {} failures: leaving dir {}".format(self.suite_name, num_errors, num_failures, temp_dir_info.dirname))
                temp_dir_info.clear = False
        
    def register_test_class(self, test_class):
        self._registered_test_classes.append(test_class)

    def test_classes_and_names(self):
        for test_class in self._registered_test_classes:
            for test_name in test_class.test_names():
                yield test_class, "{}.{}".format(self.suite_name, test_name)
        
    def test_names(self):
        for test_class, test_name in self.test_classes_and_names():
            yield test_name
        

    
    
