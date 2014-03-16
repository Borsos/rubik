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
           'fromfile_generic', 'fromfile_raw', 'fromfile_text', 'fromfile_csv']

import numpy as np

from . import conf
from .errors import CubistError
from .shape import Shape
from .selection import Selection

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

class ExtractReader(object):
    def __init__(self, dtype, shape, selection):
        self.dtype = dtype
        self.dtype_bytes = dtype().itemsize
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        self.shape = shape
        if selection is not None:
            if not isinstance(selection, Selection):
                selection = Selection(selection)
        self.selection = selection

    def read(self, input_file):
        if self.selection is None:
            return self.read_data(input_file, self.shape, self.selection)
        else:
            return self._read(input_file, self.shape, self.selection)

    def _read(self, input_file, shape, selection):
        assert isinstance(shape, Shape)
        assert isinstance(selection, Selection)
        if selection is None or len(shape) <= 1:
            return self.read_data(input_file, shape, selection)
        else:
            count, sub_count = selection.get_counts(shape)
            if sub_count < count:
                dim0, subshape = shape.split_first()
                pick0, subselection = selection.split_first()
                pick0_value = pick0.value()
                if isinstance(pick0_value, slice):
                    start, stop, step = pick0_value.indices(dim0)
                    prev_index = 0
                    subcubes = []
                    is_array = False
                    for curr_index in range(start, stop, step):
                        self.skip_data(input_file, curr_index - prev_index, subshape)
                        subcube = self._read(input_file, subshape, subselection)
                        if isinstance(subcube, np.ndarray):
                            is_array = True
                        subcubes.append(subcube)
                        prev_index = curr_index + 1
                    # skipping remaining elements:
                    self.skip_data(input_file, dim0 - prev_index, subshape)
                    if is_array:
                        return np.array(subcubes)
                    else:
                        return np.array(subcubes)
                else:
                    if pick0_value > 0:
                        self.skip_data(input_file, pick0_value, subshape)
                    cube = self._read(input_file, subshape, subselection)
                    self.skip_data(input_file, dim0 - pick0_value - 1, subshape)
                    return cube
            else:
                return self.read_data(input_file, shape, selection)

    def read_data(self, input_file, shape, selection=None):
        raise NotImplementedError()

    def skip_data(self, input_file, num_indices, shape):
        for i in range(num_indices):
            self.read_data(input_file, shape, None)

class ExtractRawCsvReader(ExtractReader):
    def __init__(self, dtype, shape, selection, sep):
        ExtractReader.__init__(self, dtype, shape, selection)
        self.sep = sep

    def read_data(self, input_file, shape, selection=None):
        cube = np.fromfile(input_file, dtype=self.dtype, count=shape.count(), sep=self.sep).reshape(shape.shape())
        if selection is not None:
            cube = cube[selection.picks()]
        return cube

class ExtractRawReader(ExtractRawCsvReader):
    def __init__(self, dtype, shape, selection):
        ExtractRawCsvReader.__init__(self, dtype, shape, selection, sep='')
    
    def skip_data(self, input_file, num_indices, shape):
        if num_indices > 0:
            skip_bytes = num_indices * shape.count() * self.dtype_bytes
            #print "skipping {0} indices, {1} elements, {2} bytes".format(num_indices, num_indices * shape.count(), skip_bytes)
            input_file.seek(skip_bytes, 1)

class ExtractCsvReader(ExtractRawCsvReader):
    def __init__(self, dtype, shape, selection, sep=conf.FILE_FORMAT_CSV_SEPARATOR):
        ExtractRawCsvReader.__init__(self, dtype, shape, selection, sep=sep)
    
class ExtractTextReader(ExtractReader):
    def __init__(self, dtype, shape, selection, delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
        ExtractReader.__init__(self, dtype, shape, selection)
        self.delimiter = delimiter

    def read(self, input_file):
        # reading a subcube is not allowed
        return self.read_data(input_file, self.shape, self.selection)

    def read_data(self, input_file, shape, selection=None):
        cube = np.loadtxt(input_file, dtype=self.dtype, delimiter=self.delimiter).reshape(shape.shape())
        if selection is not None:
            cube = cube[selection.picks()]
        return cube

def fromfile_generic(ftype, f, dtype, shape, selection=None, **n_args):
    """fromfile_generic(ftype, f, dtype, shape, selection=None) -> read a cube from raw file f with given shape and selection
    ftype can be 'raw', 'text', 'csv'
    f can be a  str or a file object
    """
    if isinstance(f, str):
        with open(f, 'rb') as f_in:
            return fromfile_generic(ftype, f_in, dtype, shape, selection, **n_args)
    else:
        if ftype == conf.FILE_FORMAT_RAW:
            ereader_class = ExtractRawReader
        elif ftype == conf.FILE_FORMAT_TEXT:
            ereader_class = ExtractTextReader
        elif ftype == conf.FILE_FORMAT_CSV:
            ereader_class = ExtractCsvReader
        else:
            raise CubistError("invalid file type {0}".format(ftype))
        ereader = ereader_class(dtype=dtype, shape=shape, selection=selection, **n_args)
        return ereader.read(f)

def fromfile_raw(f, dtype, shape, selection=None):
    """fromfile_raw(f, dtype, shape, selection=None) -> read a cube from raw file f with given shape and selection
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_RAW, f, dtype, shape, selection)

def fromfile_text(f, dtype, shape, selection=None,
        delimiter=conf.FILE_FORMAT_TEXT_DELIMITER):
    """fromfile_text(f, dtype, shape, selection=None, delimiter=conf.conf.FILE_FORMAT_TEXT_DELIMITER) -> read a cube from text file f with given shape and selection
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_TEXT, f, dtype, shape, selection, delimiter=delimiter)

def fromfile_csv(f, dtype, shape, selection=None, sep=conf.FILE_FORMAT_CSV_SEPARATOR):
    """fromfile_raw(f, dtype, shape, selection=None, sep=conf.FILE_FORMAT_CSV_SEPARATOR) -> read a cube from raw file f with given shape and selection
    f can be a  str or a file object
    """
    return fromfile_generic(conf.FILE_FORMAT_CSV, f, dtype, shape, selection, sep=sep)
