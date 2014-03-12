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

import collections

import numpy as np

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
    return getattr(np, data_type)
