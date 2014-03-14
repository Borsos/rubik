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

__all__ = ['linear_cube', 'random_cube', 'fill_cube']

import numpy as np

DEFAULT_DTYPE = np.float32

def set_default_dtype(dtype):
    global DEFAULT_DTYPE
    DEFAULT_TYPE = dtype

def _shape_count(shape):
    if shape:
        count = 1
        for dim in shape:
            count *= dim
    else:
        count = 0
    return count

def linear_cube(shape, start=0.0, increment=1.0):
    """linear_cube(shape, start=0.0, increment=1.0) -> create a cube with the given shape,
       with elements in linear sequence, starting from 'start', with increment 'increment'
    """
    count = _shape_count(shape)
    return np.array(np.linspace(start, start + increment * (count - 1), count), dtype=DEFAULT_DTYPE).reshape(shape)

def random_cube(shape):
    """random_cube(shape) -> create a cube with random elements
    """
    count = _shape_count(shape)
    cube = np.random.rand(count).reshape(shape)
    if cube.dtype != DEFAULT_DTYPE:
        return cube.astype(DEFAULT_DTYPE)
    else:
        return cube

def fill_cube(shape, value=0.0):
    """fill_cube(shape, value=0.0) -> create a cube with all elements == 'value'
    """
    count = _shape_count(shape)
    if value == 0.0:
        cube = np.zeros(count, dtype=DEFAULT_DTYPE)
    elif value == 1.0:
        cube = np.ones(count, dtype=DEFAULT_DTYPE)
    else:
        cube = np.empty(count, dtype=DEFAULT_DTYPE)
        cube.fill(value)
    return cube.reshape(shape)

