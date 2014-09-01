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

__all__ = ['fromfile_generic', 'fromfile_raw', 'fromfile_text', 'fromfile_csv',
           'write_linear_cube', 'write_random_cube', 'write_const_cube',
          ]

import numpy as np

from .internals import *
from .creation import linear_cube, random_cube, const_cube

from .. import conf
from ..py23 import irange
from ..units import Memory
from ..errors import RubikError
from ..shape import Shape
from ..extractor import Extractor
from ..asfile import asfile
from ..format_filename import format_filename

class ExtractReader(object):
    def __init__(self, dtype, shape, extractor, min_size):
        if dtype is None:
            dtype = DEFAULT_DTYPE
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

class CubeWriter(object):
    def __init__(self, file, shape, buffer_size):
        if buffer_size is None:
            buffer_size = 1024 ** 3
        buffer_count = buffer_size // DEFAULT_DTYPE().itemsize
        shape = Shape(shape)
        count = shape.count()
        if isinstance(file, str):
            file = format_filename(file, shape=shape, file_format='raw', file_dtype=DEFAULT_DTYPE)
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
    def __init__(self, file, shape, buffer_size, start, increment):
       CubeWriter.__init__(self, file=file, shape=shape, buffer_size=buffer_size)
       self.start = start
       self.increment = increment

    def create_subcube(self, par_count):
       np_array = linear_cube((par_count, ), start=self.start, increment=self.increment)
       self.start += self.increment * par_count
       return np_array
    
def write_linear_cube(file, shape, start=0.0, increment=1.0, buffer_size=None):
    """write_linear_cube(file, shape, start=0.0, increment=1.0, buffer_size=None) -> write
       a cube with the given shape to the file 'file', with elements in linear sequence,
       starting from 'start', with increment 'increment'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    output_mode_callback()
    lcw = LinearCubeWriter(file=file, shape=shape, buffer_size=buffer_size, start=start, increment=increment)
    lcw.write()
        
class RandomCubeWriter(CubeWriter):
    def __init__(self, file, shape, buffer_size, min, max):
       CubeWriter.__init__(self, file=file, shape=shape, buffer_size=buffer_size)
       self.min = min
       self.max = max

    def create_subcube(self, par_count):
        return random_cube(shape=(par_count, ), min=self.min, max=self.max)
    
def write_random_cube(file, shape, min=0.0, max=1.0, buffer_size=None):
    """write_random_cube(file, shape, min=0.0, max=1.0, buffer_size=None) -> write
       a cube with the given shape to the file 'file', with random elements
       between 'min' and 'max'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    output_mode_callback()
    rcw = RandomCubeWriter(file=file, shape=shape, buffer_size=buffer_size, min=min, max=max)
    rcw.write()
        
class ConstCubeWriter(CubeWriter):
    def __init__(self, file, shape, buffer_size, value):
       CubeWriter.__init__(self, file=file, shape=shape, buffer_size=buffer_size)
       self.value = value

    def create_subcube(self, par_count):
        return const_cube(shape=(par_count, ), value=self.value)
    
def write_const_cube(file, shape, value=0.0, buffer_size=None):
    """write_const_cube(file, shape, min=0.0, max=1.0, buffer_size=None) -> write
       a cube with the given shape to the file 'file', with all elements
       equals to 'value'.
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    output_mode_callback()
    rcw = ConstCubeWriter(file=file, shape=shape, buffer_size=buffer_size, value=value)
    rcw.write()
