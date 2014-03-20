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

__all__ = ['linear_cube', 'random_cube', 'const_cube', 'const_blocks_cube',
           'fromfile_generic', 'fromfile_raw', 'fromfile_text', 'fromfile_csv',
           'not_equals_cube', 'not_equals_num', 'not_equals',
           'equals_cube', 'equals_num', 'equals']

import numpy as np

from . import conf
from .py23 import lrange, irange
from .units import Memory
from .errors import CubistError
from .shape import Shape
from .extractor import Extractor

DEFAULT_DTYPE = np.float32

def set_default_dtype(dtype):
    global DEFAULT_DTYPE
    DEFAULT_DTYPE = dtype

def _as_default_dtype(cube):
    if cube.dtype != DEFAULT_DTYPE:
        return cube.astype(DEFAULT_DTYPE)
    else:
        return cube

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
    return _as_default_dtype(cube)

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
    return _as_default_dtype(cube)

def const_blocks_cube(shape, start=0.0, increment=1.0, block_dims=2, start_dim=None):
    """const_blocks_cube(shape, start=0.0, increment=1.0, block_dims=2, start_dim=None) ->
       create a cube with the given shape, composed by blocks filled with
       const value.  This value starts with 'start' and is incremented by
       'increment'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
       If block_dims == 1, it is equivalent to linear_cube(shape, start, increment)
       If block_dims == len(shape), it is equivalent to const_cube(shape, start)
       'start_dim' is the starting dimension for blocks. By default it is '-block_dims'.
    """
    shape = Shape(shape)
    if len(shape) == 0:
        return np.array([], dtype=DEFAULT_DTYPE)
    if block_dims < 1:
        raise CubistError("invalid block_dims={0}: must be > 0".format(block_dims))
    elif block_dims > len(shape):
        raise CubistError("invalid block_dims={0}: must be > len(shape) == {1}".format(block_dims, len(shape)))
    if start_dim is None:
       start_dim = -block_dims
    while start_dim < 0:
       start_dim += len(shape)
    if start_dim >= len(shape):
        raise CubistError("invalid start_dim={0}: must be < len(shape) == {1}".format(start_dim, len(shape)))
    end_dim = min(len(shape), start_dim + block_dims)
    shape_t = shape.shape()

    def _make_sub_block(const_count, lin_count, begin, increment):
        #print "const_count={0}, lin_count={1}, begin={2}, increment={3}".format(const_count, lin_count, begin, increment)
        if const_count:
            if lin_count:
                cube = np.array([np.arange(begin, begin + lin_count * increment, increment, dtype=DEFAULT_DTYPE) for i in irange(const_count)], dtype=DEFAULT_DTYPE)
            else:
                #cube = _make_lin(const_count, b, 0.0)
                cube = np.linspace(begin, begin, const_count)
        else:
            if lin_count:
                #cube = _make_lin(lin_count, b, increment)
                cube = np.linspace(begin, begin + lin_count * increment, lin_count)
            else:
                cube = None
        #print cube
        #if cube is None:
        #    print "-> None"
        #else:
        #    print "-> cube.size={0}".format(cube.size)
        return cube

    if len(shape_t) > block_dims:
        shape_a = Shape(shape_t[:start_dim])
        shape_b = Shape(shape_t[start_dim:end_dim])
        shape_c = Shape(shape_t[end_dim:])
        shape_a_count = shape_a.count()
        shape_b_count = shape_b.count()
        shape_c_count = shape_c.count()
        #print "start_dim={0}, block_dims={1}, end_dim={2}".format(start_dim, block_dims, end_dim)
        #print "A:", shape_a_count, repr(str(shape_a))
        #print "B:", shape_b_count, repr(str(shape_b))
        #print "C:", shape_c_count, repr(str(shape_c))
        if shape_a_count:
            b_beg = 0
            b_inc = 1
            b_end = shape_a_count
            if shape_c_count:
                b_inc *= shape_c_count
                b_end *= shape_c_count
            cube = np.array([_make_sub_block(shape_b_count, shape_c_count, b, increment) for b in irange(b_beg, b_end, b_inc)])
        else:
            cube = _make_sub_block(shape_b_count, shape_c_count, start, increment)
        cube = cube.reshape(shape.shape())
    elif len(shape_t) <= block_dims:
        return const_cube(shape, value=start)
    else:
        cube = const_cube(shape, 0.0)
    return _as_default_dtype(cube)
        
def not_equals_cube(cube_0, cube_1, tolerance=0.0):
    """not_equals_cube(cube_0, cube_1, tolerance=0.0) -> a cube with 1.0 where
           cube_0 != cube_1 within the given tolerance, 0.0 elsewhere
    """
    c = (np.abs(cube_0 - cube_1) > tolerance).astype(cube_0.dtype)
    return c

def not_equals_num(cube_0, cube_1, tolerance=0.0):
    """not_equals_num(cube_0, cube_1, tolerance=0.0) -> the number of elements
           that are != within the given tolerance
    """
    c = np.count_nonzero(not_equals_cube(cube_0, cube_1, tolerance))
    return c

def equals_cube(cube_0, cube_1, tolerance=0.0):
    """not_equals_cube(cube_0, cube_1, tolerance=0.0) -> a cube with 1.0 where
           cube_0 == cube_1 within the given tolerance, 0.0 elsewhere
    """
    c = (np.abs(cube_0 - cube_1) <= tolerance).astype(cube_0.dtype)
    return c

def equals_num(cube_0, cube_1, tolerance=0.0):
    """num__equals(cube_0, cube_1, tolerance=0.0) -> the number of elements
           that are == within the given tolerance
    """
    c = np.count_nonzero(equals_cube(cube_0, cube_1, tolerance))
    return c

def not_equals(cube_0, cube_1, tolerance=0.0):
    """not_equals(cube_0, cube_1, tolerance=0.0) -> True if cube_0 == cube_1
           within the given tolerance, False otherwise
    """
    return not_equals_num(cube_0, cube_1, tolerance) != 0


def equals(cube_0, cube_1, tolerance=0.0):
    """equals(cube_0, cube_1, tolerance=0.0) -> True if cube_0 == cube_1
           within the given tolerance, False otherwise
    """
    return equals_num(cube_0, cube_1, tolerance) != 0

class ExtractReader(object):
    def __init__(self, dtype, shape, extractor, min_size):
        self.dtype = dtype
        self.dtype_bytes = dtype().itemsize
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        self.shape = shape
        if extractor is not None:
            if not isinstance(extractor, Extractor):
                extractor = Extractor(extractor)
        self.extractor = extractor
        self.min_size = min_size
        if isinstance(min_size, Memory):
            self.min_size_bytes = min_size.get_bytes()
        else:
            self.min_size_bytes = min_size
        self.min_size_count = self.min_size_bytes / dtype().itemsize

    def read(self, input_file):
        if self.extractor is None:
            return self.read_data(input_file, self.shape, self.extractor)
        else:
            return self._read(input_file, self.shape, self.extractor)

    def _read(self, input_file, shape, extractor):
        assert isinstance(shape, Shape)
        assert isinstance(extractor, Extractor)
        if extractor is None or len(shape) <= 1:
            return self.read_data(input_file, shape, extractor)
        else:
            count, sub_count = extractor.get_counts(shape)
            #print "count={c}, sub_count={sc}, self.min_size={mc}, extractor={e}, shape={s}".format(c=count, sc=sub_count, mc=self.min_size, e=extractor, s=shape)
            if sub_count < count and count > self.min_size_count:
                #print 'reading optimized {sc} from {c}'.format(sc=sub_count, c=count)
                dim0, subshape = shape.split_first()
                index_picker0, subextractor = extractor.split_first()
                index_picker0_value = index_picker0.value()
                if isinstance(index_picker0_value, slice):
                    start, stop, step = index_picker0_value.indices(dim0)
                    prev_index = 0
                    subcubes = []
                    for curr_index in irange(start, stop, step):
                        self.skip_data(input_file, curr_index - prev_index, subshape)
                        subcube = self._read(input_file, subshape, subextractor)
                        subcubes.append(subcube)
                        prev_index = curr_index + 1
                    # skipping remaining elements:
                    self.skip_data(input_file, dim0 - prev_index, subshape)
                    return np.array(subcubes)
                else:
                    if index_picker0_value > 0:
                        self.skip_data(input_file, index_picker0_value, subshape)
                    cube = self._read(input_file, subshape, subextractor)
                    self.skip_data(input_file, dim0 - index_picker0_value - 1, subshape)
                    return cube
            else:
                #print 'reading safe {sc} from {c}'.format(sc=sub_count, c=count)
                return self.read_data(input_file, shape, extractor)

    def read_data(self, input_file, shape, extractor=None):
        raise NotImplementedError()

    def skip_data(self, input_file, num_indices, shape):
        for i in irange(num_indices):
            self.read_data(input_file, shape, None)

class ExtractRawCsvReader(ExtractReader):
    def __init__(self, dtype, shape, extractor, min_size, sep):
        ExtractReader.__init__(self, dtype, shape, extractor=extractor, min_size=min_size)
        self.sep = sep

    def read_data(self, input_file, shape, extractor=None):
        cube = np.fromfile(input_file, dtype=self.dtype, count=shape.count(), sep=self.sep).reshape(shape.shape())
        if extractor is not None:
            cube = cube[extractor.index_pickers()]
        return cube

class ExtractRawReader(ExtractRawCsvReader):
    def __init__(self, dtype, shape, extractor, min_size):
        ExtractRawCsvReader.__init__(self, dtype, shape, extractor=extractor, min_size=min_size, sep='')
    
    def skip_data(self, input_file, num_indices, shape):
        if num_indices > 0:
            skip_bytes = num_indices * shape.count() * self.dtype_bytes
            #print "skipping {0} indices, {1} elements, {2} bytes".format(num_indices, num_indices * shape.count(), skip_bytes)
            input_file.seek(skip_bytes, 1)

class ExtractCsvReader(ExtractRawCsvReader):
    def __init__(self, dtype, shape, extractor, min_size, sep=conf.FILE_FORMAT_CSV_SEPARATOR):
        ExtractRawCsvReader.__init__(self, dtype, shape, extractor=extractor, min_size=min_size, sep=sep)
    
class ExtractTextReader(ExtractReader):
    def __init__(self, dtype, shape, extractor, min_size, delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
        ExtractReader.__init__(self, dtype, shape, extractor=extractor, min_size=min_size)
        self.delimiter = delimiter

    def read(self, input_file):
        # reading a subcube is not allowed
        return self.read_data(input_file, self.shape, self.extractor)

    def read_data(self, input_file, shape, extractor=None):
        cube = np.loadtxt(input_file, dtype=self.dtype, delimiter=self.delimiter).reshape(shape.shape())
        if extractor is not None:
            cube = cube[extractor.index_pickers()]
        return cube

def fromfile_generic(ftype, f, dtype, shape, extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE, **n_args):
    """fromfile_generic(ftype, f, dtype, shape,
           extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE) ->
       read a cube from raw file f with given shape and extractor
    ftype can be 'raw', 'text', 'csv'
    f can be a  str or a file object
    when reading less than min_size bytes, switch to the safe algorithm
    """
    if isinstance(f, str):
        with open(f, 'rb') as f_in:
            return fromfile_generic(ftype, f_in, dtype, shape, extractor=extractor, min_size=min_size, **n_args)
    else:
        if ftype == conf.FILE_FORMAT_RAW:
            ereader_class = ExtractRawReader
        elif ftype == conf.FILE_FORMAT_TEXT:
            ereader_class = ExtractTextReader
        elif ftype == conf.FILE_FORMAT_CSV:
            ereader_class = ExtractCsvReader
        else:
            raise CubistError("invalid file type {0}".format(ftype))
        ereader = ereader_class(dtype=dtype, shape=shape, extractor=extractor, min_size=min_size, **n_args)
        return ereader.read(f)

def fromfile_raw(f, dtype, shape, extractor=None,
        min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE):
    """fromfile_raw(f, dtype, shape,
           extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE) ->
               read a cube from raw file f with given shape and extractor
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_RAW, f, dtype, shape, extractor=extractor, min_size=min_size)

def fromfile_text(f, dtype, shape, extractor=None, 
        min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE,
        delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
    """fromfile_text(f, dtype, shape, extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE, delimiter=conf.conf.FILE_FORMAT_TEXT_DELIMITER) -> read a cube from text file f with given shape and extractor
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_TEXT, f, dtype, shape, extractor=extractor, min_size=min_size, delimiter=delimiter)

def fromfile_csv(f, dtype, shape, extractor=None,
        min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE,
        sep=conf.FILE_FORMAT_CSV_SEPARATOR):
    """fromfile_raw(f, dtype, shape, extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE, sep=conf.FILE_FORMAT_CSV_SEPARATOR) -> read a cube from raw file f with given shape and extractor
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_CSV, f, dtype, shape, extractor=extractor, min_size=min_size, sep=sep)
