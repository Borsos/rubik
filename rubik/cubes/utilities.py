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
           'get_dtype',
           'best_precise_dtype',
           'precise_sum',
           'precise_mean',
          ]

import numpy as np
import random

from .. import conf

def get_dtype(dtype):
    """get_dtype(dtype) -> numpy dtype
       The argument dtype can be:
        * a string, such as 'float32'
        * a numpy dtype class, such as np.float32
        * a numpy dtype object, such as cube.dtype
       The return is always a numpy dtype class.
    """
    return conf.get_dtype(dtype)


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

def set_random_seed(random_seed):
    """set_random_seed(seed)
       Sets the random seed for both the numpy and random modules
    """
    np.random.seed(random_seed)
    random.seed(random_seed)

def precise_sum(cube, axis=None, dtype=None, out=None, keepdims=False):
    """precise_sum(cube, axis=None, dtype=None, out=None, keepdims=False) -> 
           precise sum of cube
       This is a replacement of numpy.sum; if dtype is None, the best precise
       dtype is used.
    """
    if dtype is None:
        dtype = best_precise_dtype(cube.dtype)
    return np.sum(a=cube, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

def precise_mean(cube, axis=None, dtype=None, out=None, keepdims=False):
    """precise_mean(cube, axis=None, dtype=None, out=None, keepdims=False) ->
           precise mean of cube
       This is a replacement of numpy.mean; if dtype is None, the best precise
       dtype is used.
    """
    if dtype is None:
        dtype = best_precise_dtype(cube.dtype)
    return np.mean(a=cube, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

