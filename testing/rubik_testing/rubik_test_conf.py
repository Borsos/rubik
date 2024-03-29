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
           'RubikTestConf',
           'RUBIK_TEST_CONF',
          ]

from .application.log import get_test_logger

class RubikTestConf(object):
    def __init__(self, logger=None, verbose_level=0, trace_errors=False):
        self.verbose_level = verbose_level
        self.trace_errors = trace_errors
        if logger is None:
            logger = get_test_logger()
        self.logger = logger

RUBIK_TEST_CONF = RubikTestConf()
