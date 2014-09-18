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
           'PROGRAM_NAME',
           'VERSION_MAJOR',
           'VERSION_MINOR',
           'VERSION_PATCH',
           'VERSION',
           'FILE_FORMAT_RAW',
           'FILE_FORMAT_CSV',
           'FILE_FORMAT_CSV_SEPARATOR',
           'FILE_FORMAT_RAW',
           'FILE_FORMAT_TEXT',
           'FILE_FORMAT_TEXT_DELIMITER',
           'FILE_FORMAT_TEXT_NEWLINE',
           'FILE_FORMAT_TEXT_CONVERTER',
           'FILE_FORMATS',
           'DEFAULT_MEMORY_LIMIT',
           'DEFAULT_READ_THRESHOLD_SIZE',
           'DEFAULT_CLOBBER'
           'DATA_TYPES',
           'DEFAULT_FILE_FORMAT',
           'DEFAULT_DATA_TYPE',
           'DEFAULT_DTYPE',
           'get_dtype',
           'get_dtype_name',
           'WARNING_RuntimeWarning',
           'WARNING_all',
           'WARNINGS',
           'enable_warnings',
          ]

import os
import sys
import warnings
import collections

import numpy as np


from .errors import RubikDataTypeError
from .units import Memory
from .py23 import BASE_STRING

#PROGRAM_NAME = os.path.basename(sys.argv[0])
PROGRAM_NAME = "rubik"

VERSION_MAJOR = 1
VERSION_MINOR = 2
VERSION_PATCH = 2
VERSION = "{major}.{minor}.{patch}".format(
    major=VERSION_MAJOR,
    minor=VERSION_MINOR,
    patch=VERSION_PATCH,
)

FILE_FORMAT_RAW = 'raw'
FILE_FORMAT_CSV = 'csv'
FILE_FORMAT_TEXT = 'text'
FILE_FORMATS = (FILE_FORMAT_RAW, FILE_FORMAT_CSV, FILE_FORMAT_TEXT)
DEFAULT_FILE_FORMAT = FILE_FORMATS[0]
FILE_FORMAT_CSV_SEPARATOR = ','
FILE_FORMAT_TEXT_DELIMITER = None
FILE_FORMAT_TEXT_NEWLINE = None
FILE_FORMAT_TEXT_CONVERTER = None

DEFAULT_MEMORY_LIMIT = Memory("0")
DEFAULT_READ_THRESHOLD_SIZE = Memory("100mb")

DEFAULT_CLOBBER = True

DATA_TYPES = collections.OrderedDict((
	("bool_",	"Boolean (True or False) stored as a byte"),
	("int_",	"Default integer type (same as C long; normally either int64 or int32)"),
	("intc",	"Identical to C int (normally int32 or int64)"),
	("intp",	"Integer used for indexing (same as C ssize_t; normally either int32 or int64)"),
	("int8",	"Byte (-128 to 127)"),
	("int16",	"Integer (-32768 to 32767)"),
	("int32",	"Integer (-2147483648 to 2147483647)"),
	("int64",	"Integer (-9223372036854775808 to 9223372036854775807)"),
	("uint8",	"Unsigned integer (0 to 255)"),
	("uint16",	"Unsigned integer (0 to 65535)"),
	("uint32",	"Unsigned integer (0 to 4294967295)"),
	("uint64",	"Unsigned integer (0 to 18446744073709551615)"),
	("float_",	"Shorthand for float64."),
	("float16",	"Half precision float: sign bit, 5 bits exponent, 10 bits mantissa"),
	("float32",	"Single precision float: sign bit, 8 bits exponent, 23 bits mantissa"),
	("float64",	"Double precision float: sign bit, 11 bits exponent, 52 bits mantissa"),
	("complex_",	"Shorthand for complex128."),
	("complex64",	"Complex number, represented by two 32-bit floats (real and imaginary components)"),
	("complex128",	"Complex number, represented by two 64-bit floats (real and imaginary components)"),
))

DEFAULT_DATA_TYPE = "float32"

def get_dtype(data_type):
    if data_type is None:
        data_type = DEFAULT_DATA_TYPE
    if isinstance(data_type, np.dtype):
        return data_type.type
    elif isinstance(data_type, BASE_STRING):
        try:
            return getattr(np, data_type)
        except Exception as err:
            raise RubikDataTypeError("invalid dtype {0!r}: {1}: {2}".format(data_type, err.__class__.__name__, err))
    else:
        if isinstance(data_type, type) and issubclass(data_type, np.generic):
            return data_type
        else:
            raise ValueError("invalid data type {!r} of type {}".format(data_type, type(data_type).__name__))

def get_dtype_name(data_type):
    dtype = get_dtype(data_type)
    return dtype.__name__

DEFAULT_DTYPE = get_dtype(DEFAULT_DATA_TYPE)

WARNING_RuntimeWarning = "RuntimeWarning"
WARNING_all = "all"
WARNINGS = (
        WARNING_RuntimeWarning,
)
ALL_WARNINGS = WARNINGS + (
        WARNING_all,
)

def enable_warnings(*warns):
    s = set(warns)
    if WARNING_all in s:
        s.update(WARNINGS)
    for warn in WARNINGS:
        if not warn in s:
            #print "disable ", warn
            warnings.filterwarnings('ignore', category=RuntimeWarning)
