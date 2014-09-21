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

import sys

from rubik.application.log import create_logger, set_verbose_level

__all__ = [
           'TEST_LOGGER',
           'get_test_logger',
           'set_test_logger',
          ]

TEST_LOGGER_NAME = "TEST"
TEST_LOGGER = None
TEST_LOGGER_VERBOSE_LEVEL = None

def set_test_logger(verbose_level, stream=None):
    global TEST_LOGGER
    global TEST_LOGGER_VERBOSE_LEVEL
    if TEST_LOGGER is None:
        TEST_LOGGER = create_logger(TEST_LOGGER_NAME, verbose_level=verbose_level, stream=stream)
    else:
        set_verbose_level(TEST_LOGGER, verbose_level)
        TEST_LOGGER_VERBOSE_LEVEL = verbose_level
    return TEST_LOGGER

def get_test_logger():
    return TEST_LOGGER

