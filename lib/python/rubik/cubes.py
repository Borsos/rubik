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
           'fromfile_generic', 'fromfile_raw', 'fromfile_text', 'fromfile_csv',
           'not_equals_cube', 'not_equals_num', 'not_equals',
           'equals_cube', 'equals_num', 'equals',
           'reldiff_cube', 'threshold_cube',
           'nonzero_cube']

import numpy as np

from . import conf
from .py23 import lrange, irange
from .units import Memory
from .errors import RubikError
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

def threshold_cube(cube, threshold=0.0, value=0.0):
    """threshold_cube(cube, threshold=0.0, value=0.0) : sets to 'value' all elements <= 'threshold'
    """
    return np.where(cube > threshold, cube, value)

def reldiff_cube(cube_0, cube_1, in_threshold=None, out_threshold=None, percentage=False):
    """reldiff(cube_0, cube_1, in_threshold=None, out_threshold=None, percentage=False) ->
    cube of relative difference
    | a - b |
    _________
       |a|
    'in_threshold': if passed, this threshold is applied to 'a' and 'b';
    'out_threshold': if passed, this threshold is applied to the output (the reldiff)
    'percentage': if True, the output is multiplied by 100.0
    """
    if in_threshold is not None:
        cube_0 = threshold_cube(cube_0, threshold=in_threshold)
        cube_1 = threshold_cube(cube_1, threshold=in_threshold)
    cube_out = np.nan_to_num(np.abs(cube_0 - cube_1) / np.abs(cube_0))
    if out_threshold is not None:
        cube_out = threshold_cube(cube_out, threshold=out_threshold)
    if percentage:
        cube_out *= 100.0
    return cube_out

def nonzero_cube(cube, tolerance=0.0):
    """nonzero_cube(cube_in, tolerance=0.0) -> a cube with 0.0 where cube_in == 0.0 within
    the given tolerance, 1.0 elsewhere"""
    if tolerance:
        return (np.abs(cube) > tolerance).astype(DEFAULT_DTYPE)
    else:
        return (cube != 0).astype(DEFAULT_DTYPE)

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
        self.min_size_count = self.min_size_bytes // dtype().itemsize

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
            raise RubikError("invalid file type {0}".format(ftype))
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
