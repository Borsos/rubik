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
import logging
import traceback

__all__ = ['create_logger', 'set_logger', 'get_logger',
           'set_report_logger', 'get_report_logger',
           'LOGGER', 'REPORT_LOGGER',
           'trace_errors',
          ]

def create_logger(logger_name, verbose_level, stream=None):
    if stream is None:
        stream = sys.stderr
    logger = logging.getLogger(logger_name)
    stream_handler = logging.StreamHandler(stream=stream)
    log_level = logging.WARNING
    if verbose_level >= 3:
        log_level = logging.DEBUG
    elif verbose_level >= 2:
        log_level = logging.INFO
    elif verbose_level >= 1:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)
    stream_handler.setLevel(logging.DEBUG)
    return logger

LOGGER = None
REPORT_LOGGER = None

PRINT = create_logger('PRINT', 10, stream=sys.stdout).info

def set_logger(verbose_level):
    global LOGGER
    LOGGER = create_logger("RUBIK", verbose_level)
    return LOGGER

def get_logger():
    if LOGGER is None:
        return create_logger("TMP", 1)
    else:
        return LOGGER

def set_report_logger(report_level):
    global REPORT_LOGGER
    REPORT_LOGGER = create_logger("REPORT", report_level)
    return REPORT_LOGGER

def get_report_logger():
    return REPORT_LOGGER

def trace_error(trace):
    err_type, err, tb = sys.exc_info()
    if trace:
        traceback.print_exception(err_type, err, tb)
    else:
        get_logger().error("error: {0}: {1}".format(err_type.__name__, err))
       
