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
           'DATA_TYPES',
           'get_dtype',
           'get_dtype_name',
           'set_default_dtype',
           'as_default_dtype',
           'as_dtype',
           'best_precise_dtype',
          ]

import collections

import numpy as np

from ..errors import RubikDataTypeError
from ..py23 import BASE_STRING

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


def get_dtype(dtype=None):
    """get_dtype(dtype=None) -> numpy dtype
       The argument dtype can be:
        * a string, such as 'float32'
        * a numpy dtype class, such as np.float32
        * a numpy dtype object, such as cube.dtype
        * None (default data type)
       The return is always a numpy dtype class.
    """
    if dtype is None:
        dtype = DEFAULT_DTYPE
    if isinstance(dtype, np.dtype):
        return dtype.type
    elif isinstance(dtype, BASE_STRING):
        try:
            return getattr(np, dtype)
        except Exception as err:
            raise RubikDataTypeError("invalid dtype {0!r}: {1}: {2}".format(dtype, err.__class__.__name__, err))
    else:
        if isinstance(dtype, type) and issubclass(dtype, np.generic):
            return dtype
        else:
            raise ValueError("invalid data type {!r} of type {}".format(dtype, type(dtype).__name__))

DEFAULT_DTYPE = get_dtype(DEFAULT_DATA_TYPE)

def get_dtype_name(dtype=None):
    """get_dtype_name(dtype) -> data type name
       The argument dtype can be:
        * a string, such as 'float32'
        * a numpy dtype class, such as np.float32
        * a numpy dtype object, such as cube.dtype
        * None (default data type)
       The return is always a numpy dtype class.
    """
    dtype = get_dtype(dtype)
    return dtype.__name__

def set_default_dtype(dtype=None):
    """set_default_dtype(dtype)
       Sets the default data type
       The argument dtype can be:
        * a string, such as 'float32'
        * a numpy dtype class, such as np.float32
        * a numpy dtype object, such as cube.dtype
        * None (default data type)
    """
    global DEFAULT_DTYPE
    global DEFAULT_DATA_TYPE
    DEFAULT_DTYPE = get_dtype(dtype)
    DEFAULT_DATA_TYPE = get_dtype_name(DEFAULT_DTYPE)

def get_default_dtype():
    """get_default_dtype() -> default data type"""
    global DEFAULT_DTYPE
    return DEFAULT_DTYPE

def as_dtype(cube, dtype=None):
    """as_dtype(cube, dtype=None) -> cube with given data type
       Returns a cube with the given dtype; it does not make a copy
       if the cube's dtype already matches.
    """
    if dtype is None:
        dtype = DEFAULT_DTYPE
    if cube.dtype != dtype:
        return cube.astype(dtype)
    else:
        return cube

def as_default_dtype(cube):
    """as_default_dtype(cube) -> cube with default data type
       Equivalent to as_dtype(cube, dtype=None)
    """
    return as_dtype(cube, DEFAULT_DTYPE)

def best_precise_dtype(dtype):
    """best_precise_dtype(dtype) -> best precise dtype
       e.g.: best_precise_dtype(np.float32) -> np.float64
             best_precise_dtype(np.int32)   -> np.int64
             best_precise_dtype(np.uint32)  -> np.uint64
    """
    dtype = get_dtype(dtype)
    if issubclass(dtype, np.signedinteger):
        return np.int64
    elif issubclass(dtype, np.unsignedinteger):
        return np.uint64
    elif issubclass(dtype, np.floating):
        return np.float64
    elif issubclass(dtype, np.complexfloating):
        return np.complex128
    else:
        return dtype


