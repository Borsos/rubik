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
           'cube_sum',
           'cube_mean',
          ]

import numpy as np

from .internals import best_dtype


def cube_sum(cube, axis=None, dtype=None, out=None, keepdims=False):
    """cube_sum(cube, axis=None, dtype=None, out=None, keepdims=False) -> sum of cube
       This is a replacement of numpy.sum; if dtype is None, the best available
       dtype is used.
    """
    if dtype is None:
        dtype = best_dtype(cube.dtype)
    return np.sum(a=cube, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

def cube_mean(cube, axis=None, dtype=None, out=None, keepdims=False):
    """cube_mean(cube, axis=None, dtype=None, out=None, keepdims=False) -> mean of cube
       This is a replacement of numpy.mean; if dtype is None, the best available
       dtype is used.
    """
    if dtype is None:
        dtype = best_dtype(cube.dtype)
    return np.mean(a=cube, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

