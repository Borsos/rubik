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
import contextlib

__all__ = [
           'STDOUT', 'get_stdout',
           'STDERR', 'get_stderr',
           'create_logger', 'set_logger', 'get_logger',
           'set_report_logger', 'get_report_logger',
           'set_test_logger', 'get_test_logger',
           'get_print_logger', 'get_print',
           'LOGGER', 'REPORT_LOGGER', 'TEST_LOGGER',
           'swap_streams',
           'trace_error',
           'set_trace_errors',
           'get_trace_errors',
          ]


STDOUT = sys.stdout
STDERR = sys.stderr

def get_stdout():
    return STDOUT

def get_stderr():
    return STDERR

def set_verbose_level(logger, verbose_level):
    log_level = logging.WARNING
    if verbose_level >= 3:
        log_level = logging.DEBUG
    elif verbose_level >= 2:
        log_level = logging.INFO
    elif verbose_level >= 1:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR
    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)

def create_logger(logger_name, verbose_level, stream=None):
    if stream is None:
        stream = STDERR
    logger_class = logging.getLoggerClass()
    logger = logger_class(logger_name)
    stream_handler = logging.StreamHandler(stream=stream)
    logger.addHandler(stream_handler)
    set_verbose_level(logger, verbose_level)
    return logger

LOGGER_NAME = "RUBIK"
REPORT_LOGGER_NAME = "REPORT"
TEST_LOGGER_NAME = "TEST"
PRINT_LOGGER_NAME = "PRINT"

LOGGER = None
LOGGER_VERBOSE_LEVEL = None
REPORT_LOGGER = None
REPORT_LOGGER_VERBOSE_LEVEL = None
TEST_LOGGER = None
TEST_LOGGER_VERBOSE_LEVEL = None

PRINT_LOGGER_VERBOSE_LEVEL = 10
PRINT_LOGGER = create_logger(PRINT_LOGGER_NAME, PRINT_LOGGER_VERBOSE_LEVEL, stream=STDERR)
PRINT = PRINT_LOGGER.info

def get_print_logger():
    return PRINT_LOGGER

def get_print():
    return PRINT

def set_logger(verbose_level, stream=None):
    global LOGGER
    global LOGGER_VERBOSE_LEVEL
    if LOGGER is None:
        LOGGER = create_logger(LOGGER_NAME, verbose_level=verbose_level, stream=stream)
    else:
        set_verbose_level(LOGGER, verbose_level)
        LOGGER_VERBOSE_LEVEL = verbose_level
    return LOGGER

def get_logger():
    if LOGGER is None:
        return create_logger("TMP", 1)
    else:
        return LOGGER

def set_report_logger(verbose_level, stream=None):
    global REPORT_LOGGER
    global REPORT_LOGGER_VERBOSE_LEVEL
    if REPORT_LOGGER is None:
        REPORT_LOGGER = create_logger(REPORT_LOGGER_NAME, verbose_level=verbose_level, stream=stream)
    else:
        set_verbose_level(REPORT_LOGGER, verbose_level)
        REPORT_LOGGER_VERBOSE_LEVEL = verbose_level
    return REPORT_LOGGER

def get_report_logger():
    return REPORT_LOGGER

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

@contextlib.contextmanager
def swap_streams(stdout, stderr):
    global STDOUT
    global STDERR
    global LOGGER
    global REPORT_LOGGER
    global PRINT_LOGGER
    global PRINT
    backup_stdout = STDOUT
    backup_stderr = STDERR
    backup_logger = LOGGER
    backup_report_logger = REPORT_LOGGER
    backup_print_logger = PRINT_LOGGER
    backup_print = PRINT
    STDERR = stderr
    STDOUT = stdout
    LOGGER = create_logger(LOGGER_NAME, LOGGER_VERBOSE_LEVEL, stream=stderr)
    REPORT_LOGGER = create_logger(REPORT_LOGGER_NAME, REPORT_LOGGER_VERBOSE_LEVEL, stream=stderr)
    PRINT_LOGGER = create_logger(PRINT_LOGGER_NAME, PRINT_LOGGER_VERBOSE_LEVEL, stream=stdout)
    PRINT = PRINT_LOGGER.info
    #print id(backup_logger), id(LOGGER)
    #raw_input("...")
    yield
    LOGGER = backup_logger
    REPORT_LOGGER = backup_report_logger
    PRINT_LOGGER = backup_print_logger
    PRINT = backup_print
    STDOUT = backup_stdout
    STDERR = backup_stderr
    

DEFAULT_TRACE_ERRORS = False

def set_trace_errors(trace):
    global DEFAULT_TRACE_ERRORS
    DEFAULT_TRACE_ERRORS = trace

def get_trace_errors():
    global DEFAULT_TRACE_ERRORS
    return DEFAULT_TRACE_ERRORS

def trace_error(trace=None, exc_info=None):
    if trace is None:
        trace = DEFAULT_TRACE_ERRORS
    if exc_info is None:
        exc_info = sys.exc_info()
    err_type, err, tb = exc_info
    if trace:
        traceback.print_exception(err_type, err, tb)
    else:
        get_logger().error("error: {0}: {1}".format(err_type.__name__, err))
       
