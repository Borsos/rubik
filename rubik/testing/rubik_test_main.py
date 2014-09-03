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

from ..application.log import get_logger
from ..cubes.api import set_random_seed

from .rubik_test_runner import RubikTestRunner
from .rubik_test_suite import RubikTestSuite

from .tests import SUITES

from rubik.testing.tests import SUITES


class RubikTestMain(object):
    def __init__(self, logger=None):
        if logger is None: 
            logger = conf.get_logger()
        self.logger = logger
        self.name = self.__class__.__name__

        # global setup
        set_random_seed(100)
    
        # create runner
        self.rubik_test_runner = RubikTestRunner()

        # create suite
        self.rubik_test_suite = RubikTestSuite()

        # add suites
        for suite_name, suite in SUITES.iteritems():
            self.logger.info("{}: adding suite {!r}:".format(self.name, suite_name))
            self.rubik_test_suite.addTest(suite)

    def run(self):
        # run tests
        self.result = self.rubik_test_runner.run(self.rubik_test_suite)
        return self.result
    
