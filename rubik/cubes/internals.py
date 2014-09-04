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
           'output_mode_callback',
           'get_output_mode_callback',
           'set_output_mode_callback',
           'set_default_dtype',
           'as_default_dtype',
           'as_dtype',
           'get_default_dtype',
           'get_dtype',
           'set_random_seed',
          ]

import random
import numpy as np
from .. import conf

OUTPUT_MODE_CALLBACK = None
DEFAULT_DTYPE = conf.DEFAULT_DTYPE

def set_output_mode_callback(callback):
    global OUTPUT_MODE_CALLBACK
    OUTPUT_MODE_CALLBACK = callback

def get_output_mode_callback():
    global OUTPUT_MODE_CALLBACK
    return OUTPUT_MODE_CALLBACK
    
def output_mode_callback():
    global OUTPUT_MODE_CALLBACK
    if OUTPUT_MODE_CALLBACK is not None:
        OUTPUT_MODE_CALLBACK()

def set_default_dtype(dtype):
    global DEFAULT_DTYPE
    DEFAULT_DTYPE = dtype

def get_default_dtype():
    global DEFAULT_DTYPE
    return DEFAULT_DTYPE

def get_dtype(dtype):
    return conf.get_dtype(dtype)

def best_dtype(dtype):
    """best_dtype(dtype) -> best dtype
       e.g.: best_dtype(np.float32) -> np.float64
             best_dtype(np.int32) -> np.int64
             best_dtype(np.uint32) -> np.uint64
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

def as_dtype(cube, dtype=None):
    if dtype is None:
        dtype = DEFAULT_DTYPE
    if cube.dtype != dtype:
        return cube.astype(dtype)
    else:
        return cube

def as_default_dtype(cube):
    return as_dtype(cube, DEFAULT_DTYPE)

def set_random_seed(random_seed):
    np.random.seed(random_seed)
    random.seed(random_seed)

