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

import sys
import logging
import traceback

def create_logger(logger_name, verbose_level):
    logger = logging.getLogger(logger_name)
    stream_handler = logging.StreamHandler()
    log_level = logging.WARNING
    if verbose_level >= 2:
        log_level = logging.DEBUG
    elif verbose_level >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)
    stream_handler.setLevel(logging.DEBUG)

    return logger

LOGGER = None

PRINT = create_logger('PRINT', 10).info

def set_logger(verbose_level):
    global LOGGER
    LOGGER = create_logger("SUBCUBE", verbose_level)
    return LOGGER

def get_logger():
    return LOGGER

def trace_error(trace):
    err_type, err, tb = sys.exc_info()
    if trace:
        traceback.print_exception(err_type, err, tb)
    else:
        get_logger().error("error: {0}: {1}".format(err_type, err))
       
