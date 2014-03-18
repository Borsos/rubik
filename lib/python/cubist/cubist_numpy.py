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

__all__ = ['linear_cube', 'random_cube', 'fill_cube',
           'fromfile_generic', 'fromfile_raw', 'fromfile_text', 'fromfile_csv',
           'num_not_equals', 'num_equals', 'not_equals', 'equals']

import numpy as np

from . import conf
from .errors import CubistError
from .shape import Shape
from .extractor import Extractor

DEFAULT_DTYPE = np.float32

def set_default_dtype(dtype):
    global DEFAULT_DTYPE
    DEFAULT_TYPE = dtype

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

def random_cube(shape):
    """random_cube(shape) -> create a cube with random elements
       The 'shape' can be a tuple (for instance, '(8, 10)') or a string
       (for instance, "8x10")
    """
    shape = Shape(shape)
    count = shape.count()
    cube = np.random.rand(count).reshape(shape.shape())
    if cube.dtype != DEFAULT_DTYPE:
        return cube.astype(DEFAULT_DTYPE)
    else:
        return cube

def fill_cube(shape, value=0.0):
    """fill_cube(shape, value=0.0) -> create a cube with all elements == 'value'
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
    return cube.reshape(shape.shape())

def cube_not_equals(cube_0, cube_1, tolerance=0.0):
    """cube_not_equals(cube_0, cube_1, tolerance=0.0) -> a cube with 1.0 where
           cube_0 != cube_1 within the given tolerance, 0.0 elsewhere
    """
    c = (np.abs(cube_0 - cube_1) > tolerance).astype(cube_0.dtype)
    return c

def num_not_equals(cube_0, cube_1, tolerance=0.0):
    """num_not_equals(cube_0, cube_1, tolerance=0.0) -> the number of elements
           that are != within the given tolerance
    """
    c = np.count_nonzero(cube_not_equals(cube_0, cube_1, tolerance))
    return c

def cube_equals(cube_0, cube_1, tolerance=0.0):
    """cube_not_equals(cube_0, cube_1, tolerance=0.0) -> a cube with 1.0 where
           cube_0 == cube_1 within the given tolerance, 0.0 elsewhere
    """
    c = (np.abs(cube_0 - cube_1) <= tolerance).astype(cube_0.dtype)
    return c

def num_equals(cube_0, cube_1, tolerance=0.0):
    """num__equals(cube_0, cube_1, tolerance=0.0) -> the number of elements
           that are == within the given tolerance
    """
    c = np.count_nonzero(cube_equals(cube_0, cube_1, tolerance))
    return c

def not_equals(cube_0, cube_1, tolerance=0.0):
    """not_equals(cube_0, cube_1, tolerance=0.0) -> True if cube_0 == cube_1
           within the given tolerance, False otherwise
    """
    return num_not_equals(cube_0, cube_1, tolerance) != 0


def equals(cube_0, cube_1, tolerance=0.0):
    """equals(cube_0, cube_1, tolerance=0.0) -> True if cube_0 == cube_1
           within the given tolerance, False otherwise
    """
    return num_equals(cube_0, cube_1, tolerance) != 0

class ExtractReader(object):
    def __init__(self, dtype, shape, extractor):
        self.dtype = dtype
        self.dtype_bytes = dtype().itemsize
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        self.shape = shape
        if extractor is not None:
            if not isinstance(extractor, Extractor):
                extractor = Extractor(extractor)
        self.extractor = extractor

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
            if sub_count < count:
                dim0, subshape = shape.split_first()
                index_picker0, subextractor = extractor.split_first()
                index_picker0_value = index_picker0.value()
                if isinstance(index_picker0_value, slice):
                    start, stop, step = index_picker0_value.indices(dim0)
                    prev_index = 0
                    subcubes = []
                    for curr_index in range(start, stop, step):
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
                return self.read_data(input_file, shape, extractor)

    def read_data(self, input_file, shape, extractor=None):
        raise NotImplementedError()

    def skip_data(self, input_file, num_indices, shape):
        for i in range(num_indices):
            self.read_data(input_file, shape, None)

class ExtractRawCsvReader(ExtractReader):
    def __init__(self, dtype, shape, extractor, sep):
        ExtractReader.__init__(self, dtype, shape, extractor)
        self.sep = sep

    def read_data(self, input_file, shape, extractor=None):
        cube = np.fromfile(input_file, dtype=self.dtype, count=shape.count(), sep=self.sep).reshape(shape.shape())
        if extractor is not None:
            cube = cube[extractor.index_pickers()]
        return cube

class ExtractRawReader(ExtractRawCsvReader):
    def __init__(self, dtype, shape, extractor):
        ExtractRawCsvReader.__init__(self, dtype, shape, extractor, sep='')
    
    def skip_data(self, input_file, num_indices, shape):
        if num_indices > 0:
            skip_bytes = num_indices * shape.count() * self.dtype_bytes
            #print "skipping {0} indices, {1} elements, {2} bytes".format(num_indices, num_indices * shape.count(), skip_bytes)
            input_file.seek(skip_bytes, 1)

class ExtractCsvReader(ExtractRawCsvReader):
    def __init__(self, dtype, shape, extractor, sep=conf.FILE_FORMAT_CSV_SEPARATOR):
        ExtractRawCsvReader.__init__(self, dtype, shape, extractor, sep=sep)
    
class ExtractTextReader(ExtractReader):
    def __init__(self, dtype, shape, extractor, delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
        ExtractReader.__init__(self, dtype, shape, extractor)
        self.delimiter = delimiter

    def read(self, input_file):
        # reading a subcube is not allowed
        return self.read_data(input_file, self.shape, self.extractor)

    def read_data(self, input_file, shape, extractor=None):
        cube = np.loadtxt(input_file, dtype=self.dtype, delimiter=self.delimiter).reshape(shape.shape())
        if extractor is not None:
            cube = cube[extractor.index_pickers()]
        return cube

def fromfile_generic(ftype, f, dtype, shape, extractor=None, **n_args):
    """fromfile_generic(ftype, f, dtype, shape, extractor=None) -> read a cube from raw file f with given shape and extractor
    ftype can be 'raw', 'text', 'csv'
    f can be a  str or a file object
    """
    if isinstance(f, str):
        with open(f, 'rb') as f_in:
            return fromfile_generic(ftype, f_in, dtype, shape, extractor, **n_args)
    else:
        if ftype == conf.FILE_FORMAT_RAW:
            ereader_class = ExtractRawReader
        elif ftype == conf.FILE_FORMAT_TEXT:
            ereader_class = ExtractTextReader
        elif ftype == conf.FILE_FORMAT_CSV:
            ereader_class = ExtractCsvReader
        else:
            raise CubistError("invalid file type {0}".format(ftype))
        ereader = ereader_class(dtype=dtype, shape=shape, extractor=extractor, **n_args)
        return ereader.read(f)

def fromfile_raw(f, dtype, shape, extractor=None):
    """fromfile_raw(f, dtype, shape, extractor=None) -> read a cube from raw file f with given shape and extractor
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_RAW, f, dtype, shape, extractor)

def fromfile_text(f, dtype, shape, extractor=None,
        delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
    """fromfile_text(f, dtype, shape, extractor=None, delimiter=conf.conf.FILE_FORMAT_TEXT_DELIMITER) -> read a cube from text file f with given shape and extractor
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_TEXT, f, dtype, shape, extractor, delimiter=delimiter)

def fromfile_csv(f, dtype, shape, extractor=None, sep=conf.FILE_FORMAT_CSV_SEPARATOR):
    """fromfile_raw(f, dtype, shape, extractor=None, sep=conf.FILE_FORMAT_CSV_SEPARATOR) -> read a cube from raw file f with given shape and extractor
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_CSV, f, dtype, shape, extractor, sep=sep)
