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
           'write_linear_cube', 'write_random_cube', 'write_const_cube',
           'join',
          ]

import numpy as np

from .internals import output_mode_callback
from .dtypes import as_dtype, get_dtype
from .utilities import interpolate_filename

from ..py23 import irange, BASE_STRING
from ..errors import RubikError
from ..shape import Shape
from ..asfile import asfile

def linear_cube(shape, start=0.0, increment=1.0, dtype=None):
    """linear_cube(shape, start=0.0, increment=1.0, dtype=None) -> create a cube
       with the given shape, with elements in linear sequence, starting from
       'start', with increment 'increment'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    dtype = get_dtype(dtype)
    return np.array(np.linspace(start, start + increment * (count - 1), count), dtype=dtype).reshape(shape.shape())

def random_cube(shape, min=0.0, max=1.0, dtype=None):
    """random_cube(shape, min=0.0, max=1.0, dtype=None) -> create a cube with
       random elements between 'min' and 'max'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    dtype = get_dtype(dtype)
    cube = np.random.rand(count).reshape(shape.shape())
    if min != 0.0 or max != 1.0:
        cube = min + cube * (max - min)
    return as_dtype(cube, dtype)

def const_cube(shape, value=0.0, dtype=None):
    """const_cube(shape, value=0.0, dtype=None) -> create a cube with all
       elements == 'value'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    dtype = get_dtype(dtype)
    if value == 0.0:
        cube = np.zeros(count, dtype=dtype)
    elif value == 1.0:
        cube = np.ones(count, dtype=dtype)
    else:
        cube = np.empty(count, dtype=dtype)
        cube.fill(value)
    cube = cube.reshape(shape.shape())
    return as_dtype(cube, dtype)

def const_blocks_cube(shape, start=0.0, increment=1.0, const_dims=(-2, -1), dtype=None):
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
    dtype = get_dtype(dtype)
    rank = shape.rank()
    if rank <= 0:
        return np.array([], dtype=dtype)
    cdims = []
    for cdim in const_dims:
        while cdim < 0:
            cdim += len(shape)
        cdims.append(cdim)
        if cdim >= rank:
            raise RubikError("invalid dimension index {0}: max is {1} since shape is {2}".format(cdim, rank - 1, shape))
    const_dims = cdims

    if not const_dims:
        return linear_cube(shape, start=start, increment=increment, dtype=dtype)

    def _make_cube(d_index, c_shape, c_start, c_increment, c_const_dims, dtype):
        if c_shape.rank() == 1:
            if d_index in c_const_dims:
                cube = const_cube(c_shape.shape(), value=c_start, dtype=dtype)
                next_start = c_start + increment
            else:
                cube = linear_cube(c_shape.shape(), start=c_start, increment=c_increment, dtype=dtype)
                next_start = c_start + increment * cube.size
            return next_start, cube
        else:
            l = []
            d_num, s_shape = c_shape.split_first()
            r_start = c_start
            n_start = c_start
            for i in irange(d_num):
                x_start, cube = _make_cube(d_index + 1, s_shape, r_start, increment, c_const_dims, dtype=dtype)
                if d_index not in c_const_dims:
                    r_start = x_start
                n_start = x_start
                l.append(cube)
            return n_start, np.array(l, dtype=dtype)
          
    next_start, cube = _make_cube(0, shape, start, increment, const_dims, dtype=dtype)
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

class CubeWriter(object):
    def __init__(self, file, shape, buffer_size, dtype=None):
        dtype = get_dtype(dtype)
        if buffer_size is None:
            buffer_size = 1024 ** 3
        buffer_count = buffer_size // dtype().itemsize
        shape = Shape(shape)
        count = shape.count()
        self.dtype = dtype
        if isinstance(file, BASE_STRING):
            file = interpolate_filename(file, shape=shape, dtype=self.dtype, file_format='raw')
        self.buffer_size = buffer_size
        self.buffer_count = buffer_count
        self.count = count
        self.shape = shape
        self.file = file

    def write(self):
        rem = self.count
        with asfile(self.file, 'wb') as f_out:
            while rem:
                par_count = max(1, min(rem, self.buffer_count))
                np_array = self.create_subcube(par_count)
                np_array.tofile(f_out)
                rem -= par_count
        
    def create_subcube(self, par_count):
       raise NotImplementedError()

class LinearCubeWriter(CubeWriter):
    def __init__(self, file, shape, buffer_size, start, increment, dtype=None):
       CubeWriter.__init__(self, file=file, shape=shape, buffer_size=buffer_size, dtype=dtype)
       self.start = start
       self.increment = increment

    def create_subcube(self, par_count):
       np_array = linear_cube((par_count, ), start=self.start, increment=self.increment, dtype=self.dtype)
       self.start += self.increment * par_count
       return np_array
    
def write_linear_cube(file, shape, start=0.0, increment=1.0, buffer_size=None, dtype=None):
    """write_linear_cube(file, shape, start=0.0, increment=1.0, buffer_size=None, dtype=None) -> write
       a cube with the given shape to the file 'file', with elements in linear sequence,
       starting from 'start', with increment 'increment'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    output_mode_callback()
    lcw = LinearCubeWriter(file=file, shape=shape, buffer_size=buffer_size, start=start, increment=increment, dtype=dtype)
    lcw.write()
        
class RandomCubeWriter(CubeWriter):
    def __init__(self, file, shape, buffer_size, min, max, dtype=None):
       CubeWriter.__init__(self, file=file, shape=shape, buffer_size=buffer_size, dtype=dtype)
       self.min = min
       self.max = max

    def create_subcube(self, par_count):
        return random_cube(shape=(par_count, ), min=self.min, max=self.max, dtype=self.dtype)
    
def write_random_cube(file, shape, min=0.0, max=1.0, buffer_size=None, dtype=None):
    """write_random_cube(file, shape, min=0.0, max=1.0, buffer_size=None, dtype=None) -> write
       a cube with the given shape to the file 'file', with random elements
       between 'min' and 'max'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    output_mode_callback()
    rcw = RandomCubeWriter(file=file, shape=shape, buffer_size=buffer_size, min=min, max=max, dtype=dtype)
    rcw.write()
        
class ConstCubeWriter(CubeWriter):
    def __init__(self, file, shape, buffer_size, value, dtype=None):
       CubeWriter.__init__(self, file=file, shape=shape, buffer_size=buffer_size, dtype=dtype)
       self.value = value

    def create_subcube(self, par_count):
        return const_cube(shape=(par_count, ), value=self.value, dtype=self.dtype)
    
def write_const_cube(file, shape, value=0.0, buffer_size=None, dtype=None):
    """write_const_cube(file, shape, min=0.0, max=1.0, buffer_size=None, dtype=None) -> write
       a cube with the given shape to the file 'file', with all elements
       equals to 'value'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    output_mode_callback()
    rcw = ConstCubeWriter(file=file, shape=shape, buffer_size=buffer_size, value=value, dtype=dtype)
    rcw.write()

