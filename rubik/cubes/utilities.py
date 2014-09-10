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
           'precise_sum',
           'precise_mean',
           'interpolate_filename',
          ]

import numpy as np
import random

from .dtypes import best_precise_dtype, get_dtype
from ..shape import Shape

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


def interpolate_filename(filename, shape, dtype, file_format, keywords=None):
    if file_format is None:
        file_format = DEFAULT_FILE_FORMAT
    dtype = get_dtype(dtype)
    if keywords is None:
        keywords = {}
    count = 0
    if shape:
        count = 1
        for i in shape:
            count *= i
    else:
        count = 0
    if not isinstance(shape, Shape):
        shape = Shape(shape)
    return filename.format(
        shape=shape,
        rank=len(shape),
        count=count,
        format=file_format,
        dtype=dtype.__name__,
        **keywords
    )
