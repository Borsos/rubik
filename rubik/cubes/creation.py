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

__all__ = ['linear_cube', 'random_cube', 'const_cube', 'const_blocks_cube',
           'join',
          ]

import numpy as np

from .settings import *

from ..py23 import irange
from ..errors import RubikError
from ..shape import Shape

def linear_cube(shape, start=0.0, increment=1.0):
    """linear_cube(shape, start=0.0, increment=1.0) -> create a cube with the
       given shape, with elements in linear sequence, starting from 'start',
       with increment 'increment'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    return np.array(np.linspace(start, start + increment * (count - 1), count), dtype=DEFAULT_DTYPE).reshape(shape.shape())

def random_cube(shape, min=0.0, max=1.0):
    """random_cube(shape, min=0.0, max=1.0) -> create a cube with random elements
       between 'min' and 'max'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    cube = np.random.rand(count).reshape(shape.shape())
    if min != 0.0 or max != 1.0:
        cube = min + cube * (max - min)
    return as_default_dtype(cube)

def const_cube(shape, value=0.0):
    """const_cube(shape, value=0.0) -> create a cube with all elements == 'value'
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    if value == 0.0:
        cube = np.zeros(count, dtype=DEFAULT_DTYPE)
    elif value == 1.0:
        cube = np.ones(count, dtype=DEFAULT_DTYPE)
    else:
        cube = np.empty(count, dtype=DEFAULT_DTYPE)
        cube.fill(value)
    cube = cube.reshape(shape.shape())
    return as_default_dtype(cube)

def const_blocks_cube(shape, start=0.0, increment=1.0, const_dims=(-2, -1)):
    """const_blocks_cube(shape, start=0.0, increment=1.0, const_dims=None) ->
       create a cube with the given shape; each subblock on the given list
       'const_dims' is constant. For instance, if len(shape) is 4 and 
       const_dims is [1, 3], then the resulting cube has subcubes _r[d0, :, d2, :]
       for any value (d0, d2); moreover, for any different value (d0, d2),
       the const subcube is filled with a different value, which is start
       for (0, 0), start + increment for (0, 1), start + 2 * increment for
       (0, 2), and so on.
    """
    shape = Shape(shape)
    count = shape.count()
    rank = shape.rank()
    if rank <= 0:
        return np.array([], dtype=DEFAULT_DTYPE)
    cdims = []
    for cdim in const_dims:
        while cdim < 0:
            cdim += len(shape)
        cdims.append(cdim)
        if cdim >= rank:
            raise RubikError("invalid dimension index {0}: max is {1} since shape is {2}".format(cdim, rank - 1, shape))
    const_dims = cdims

    if not const_dims:
        return linear_cube(shape, start=start, increment=increment)

    def _make_cube(d_index, c_shape, c_start, c_increment, c_const_dims):
        if c_shape.rank() == 1:
            if d_index in c_const_dims:
                cube = const_cube(c_shape.shape(), value=c_start)
                next_start = c_start + increment
            else:
                cube = linear_cube(c_shape.shape(), start=c_start, increment=c_increment)
                next_start = c_start + increment * cube.size
            return next_start, cube
        else:
            l = []
            d_num, s_shape = c_shape.split_first()
            r_start = c_start
            n_start = c_start
            for i in irange(d_num):
                x_start, cube = _make_cube(d_index + 1, s_shape, r_start, increment, c_const_dims)
                if d_index not in c_const_dims:
                    r_start = x_start
                n_start = x_start
                l.append(cube)
            return n_start, np.array(l, dtype=DEFAULT_DTYPE)
          
    next_start, cube = _make_cube(0, shape, start, increment, const_dims)
    return cube

def join(cubes):
    """join(cubes) -> join cubes
    Input cubes must have all the same shape"""
    if cubes:
        s0 = cubes[0].shape
        for cube in cubes[1:]:
            if s0 != cube.shape:
                raise RubikError("join: input cubes with different shapes: {} and {}".format(s0, cube.shape))
    return np.array(cubes)
