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

__all__ = ['read_cube', 'read_cube_raw', 'read_cube_text', 'read_cube_csv',
           'write_cube', 'write_cube_raw', 'write_cube_text', 'write_cube_csv',
          ]

import numpy as np

from .internals import output_mode_callback
from .dtypes import get_dtype
from .utilities import interpolate_filename
from .creation import linear_cube, random_cube, const_cube

from .. import conf
from ..py23 import irange, BASE_STRING
from ..units import Memory
from ..errors import RubikError
from ..shape import Shape
from ..extractor import Extractor
from ..asfile import asfile

class ExtractReader(object):
    def __init__(self, dtype, shape, extractor, min_size):
        dtype = get_dtype(dtype)
        self.dtype = dtype
        self.dtype_bytes = dtype().itemsize
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        self.shape = shape
        if extractor is not None:
            if not isinstance(extractor, Extractor):
                extractor = Extractor(extractor)
        self.extractor = extractor
        self.min_size = Memory(min_size)
        self.min_size_bytes = min_size.get_bytes()
        self.min_size_count = min(1, self.min_size_bytes // dtype().itemsize)

    def read(self, input_file):
        if self.extractor is None or self.min_size_bytes  <= 0:
            return self.read_data(input_file, self.shape, self.extractor)
        else:
            return self.impl_read(input_file, self.shape, self.extractor)

    def impl_read(self, input_file, shape, extractor):
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
                        subcube = self.impl_read(input_file, subshape, subextractor)
                        subcubes.append(subcube)
                        prev_index = curr_index + 1
                    # skipping remaining elements:
                    self.skip_data(input_file, dim0 - prev_index, subshape)
                    return np.array(subcubes)
                else:
                    if index_picker0_value > 0:
                        self.skip_data(input_file, index_picker0_value, subshape)
                    cube = self.impl_read(input_file, subshape, subextractor)
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
        cube = np.fromfile(input_file, dtype=self.dtype, count=shape.count(), sep=self.sep)
        cube = cube.reshape(shape.shape())
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

def read_cube(file_format, file, shape, dtype=None, extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE, **n_args):
    """read_cube(file_format, file, shape, dtype=None,
           extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE) ->
       read a cube from raw file file with given shape and extractor
       file_format can be 'raw', 'text', 'csv'
       file can be a  str or a file object
       when reading less than min_size bytes, switch to the safe algorithm
    """
    if not isinstance(shape, Shape):
        shape = Shape(shape)
    if isinstance(file, BASE_STRING):
        filename = interpolate_filename(file, shape=shape, dtype=dtype, file_format=file_format)
        with open(filename, 'rb') as f_in:
            return read_cube(file_format=file_format, file=f_in, shape=shape, dtype=dtype, extractor=extractor, min_size=min_size, **n_args)
    else:
        if file_format == conf.FILE_FORMAT_RAW:
            ereader_class = ExtractRawReader
        elif file_format == conf.FILE_FORMAT_TEXT:
            ereader_class = ExtractTextReader
        elif file_format == conf.FILE_FORMAT_CSV:
            ereader_class = ExtractCsvReader
        else:
            raise RubikError("invalid file format {0}".format(file_format))
        ereader = ereader_class(dtype=dtype, shape=shape, extractor=extractor, min_size=min_size, **n_args)
        return ereader.read(file)

def read_cube_raw(file, shape, dtype=None, extractor=None,
        min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE):
    """read_cube_raw(file, shape, dtype=None,
           extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE) ->
               read a cube from raw file file with given shape and extractor
       file can be a  str or a file object
    """
    return read_cube(
        file_format=conf.FILE_FORMAT_RAW,
        file=file,
        dtype=dtype,
        shape=shape,
        extractor=extractor,
        min_size=min_size)

def read_cube_text(file, shape, dtype=None, extractor=None, 
        min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE,
        delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
    """read_cube_text(file, shape, dtype=None,
                     extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE,
                     delimiter=conf.conf.FILE_FORMAT_TEXT_DELIMITER) ->
       read a cube from text file file with given shape and extractor
       file can be a  str or a file object
    """
    return read_cube(
        file_format=conf.FILE_FORMAT_TEXT,
        file=file,
        dtype=dtype,
        shape=shape,
        extractor=extractor,
        min_size=min_size,
        delimiter=delimiter)

def read_cube_csv(file, shape, dtype=None, extractor=None,
        min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE,
        sep=conf.FILE_FORMAT_CSV_SEPARATOR):
    """read_cube_raw(file, shape, dtype=None,
                    extractor=None, min_size=conf.DEFAULT_OPTIMIZED_MIN_SIZE,
                    sep=conf.FILE_FORMAT_CSV_SEPARATOR) -> read a cube from
       CSV file file with given shape and extractor
       file can be a  str or a file object
    """
    return read_cube(
        file_format=conf.FILE_FORMAT_CSV,
        file=file,
        dtype=dtype,
        shape=shape,
        extractor=extractor,
        min_size=min_size,
        sep=sep)

def write_cube(file_format, cube, file):
    """write_cube(cube, file) -> write cube to file with file format 'file_format'
    """
    output_mode_callback()
    if file_format == 'raw':
        return write_cube_raw(cube, file)
    elif file_format == 'csv':
        return write_cube_csv(cube, file)
    elif file_format == 'text':
        return write_cube_text(cube, file)
    else:
        raise RubikError("invalid file format {0}".format(file_format))

def write_cube_raw(cube, file):
    """write_cube_raw(cube, file) -> write cube to raw file
    """
    output_mode_callback()
    if isinstance(file, BASE_STRING):
        file = interpolate_filename(file, shape=Shape(cube.shape), dtype=cube.dtype, file_format='raw')
    cube.tofile(file)

def write_cube_csv(cube, file, separator=None):
    """write_cube_csv(cube, file, separator=None) -> write cube to csv file
    """
    output_mode_callback()
    if isinstance(file, BASE_STRING):
        file = interpolate_filename(file, shape=Shape(cube.shape), dtype=cube.dtype, file_format='csv')
    if separator is None:
        separator = conf.FILE_FORMAT_CSV_SEPARATOR
    cube.tofile(file, sep=separator)

def write_cube_text(cube, file, delimiter=None, newline=None, converter=None):
    """write_cube_text(cube, file, delimiter=" ", newline="\n", converter=None) -> write cube to text file
    """
    output_mode_callback()
    if isinstance(file, BASE_STRING):
        file = interpolate_filename(file, shape=Shape(cube.shape), dtype=cube.dtype, file_format='text')
    n_args = {}
    if delimiter is not None:
        n_args['delimiter'] = conf.FILE_FORMAT_TEXT_DELIMITER
    if newline is not None:
        n_args['newline'] = conf.FILE_FORMAT_TEXT_NEWLINE
    if converter is not None:
        n_args['fmt'] = conf.FILE_FORMAT_TEXT_CONVERTER
    np.savetxt(file, cube, **n_args)

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

