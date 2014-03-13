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

import os
import numpy as np

from . import data_types
from .application import log
from .errors import CubistError
from .shape import Shape
from .selection import Selection

class Cubist(object):
    CREATION_MODE_RANDOM = 'random'
    CREATION_MODE_RANGE = 'range'
    CREATION_MODE_ZEROS = 'zeros'
    CREATION_MODE_ONES = 'ones'
    CREATION_MODES = (CREATION_MODE_RANDOM, CREATION_MODE_RANGE, CREATION_MODE_ZEROS, CREATION_MODE_ONES)
    FILE_FORMAT_RAW = 'raw'
    FILE_FORMAT_CSV = 'csv'
    FILE_FORMAT_TEXT = 'text'
    FILE_FORMATS = (FILE_FORMAT_RAW, FILE_FORMAT_CSV, FILE_FORMAT_TEXT)
    DEFAULT_FILE_FORMAT = FILE_FORMATS[0]
    FILE_FORMAT_CSV_SEPARATOR = ','
    def __init__(self,
            data_type,
            logger,
            input_csv_separator=FILE_FORMAT_CSV_SEPARATOR,
            output_csv_separator=FILE_FORMAT_CSV_SEPARATOR,
            accept_bigger_raw_files=False):
        self.data_type = data_type
        self.dtype = data_types.get_dtype(data_type)
        self.dtype_bytes = self.dtype().itemsize
        self.logger = logger
        self.input_csv_separator = input_csv_separator
        self.output_csv_separator = output_csv_separator
        self.accept_bigger_raw_files = accept_bigger_raw_files

    def format_filename(self, filename, shape, file_format):
        count = 0
        if shape:
            count = 1
            for i in shape:
                count *= i
        else:
            count = 0
        return filename.format(
            shape="x".join(str(i) for i in shape),
            count=count,
            format=file_format,
            data_type=self.data_type,
        )

    def read(self, shape, input_format, input_filename):
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        expected_input_count = shape.count()
        numpy_function_name = None
        numpy_function_args = {}
        if input_format == self.FILE_FORMAT_RAW:
            num_bytes = shape.count() * self.dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
            # read only expected elements (number of elements already checked)
            numpy_function_name = 'fromfile'
            numpy_function_args['count'] = expected_input_count
        elif input_format == self.FILE_FORMAT_CSV:
            msg_bytes = ''
            # read all elements (must check number of elements)
            numpy_function_name = 'fromfile'
            numpy_function_args['sep'] = self.input_csv_separator
        elif input_format == self.FILE_FORMAT_TEXT:
            msg_bytes = ''
            # read all elements (must check number of elements)
            numpy_function_name = 'loadtxt'
        else:
            raise CubistError("invalid file format {0!r}".format(input_format))
        input_filename = self.format_filename(input_filename, shape.shape(), input_format)
        input_filename = self._check_input_filename(shape, input_format, input_filename)
        self.logger.info("reading {c} {t!r} elements {b}from {f!r} file {i!r}...".format(
            c=expected_input_count,
            t=self.data_type,
            b=msg_bytes,
            f=input_format,
            i=input_filename))
        array = getattr(np, numpy_function_name)(input_filename, dtype=self.dtype, **numpy_function_args)
        input_count = array.size
        if array.size != expected_input_count:
            if input_count < expected_input_count:
                raise CubistError("input file {0} is not big enough: it contains {1} elements, expected {2} elements".format(
                    input_filename,
                    input_count,
                    expected_input_count,
                ))
            elif input_count > expected_input_count:
                message = "input file {0} is greater than expected: {1} elements found, {2} elements expected".format(
                    input_filename,
                    input_count,
                    expected_input_count,
                )
                if self.accept_bigger_raw_files:
                    self.logger.warning("warning: " + message)
                else:
                    raise CubistError(message)
                array.resize(shape.shape())
        try:
            cube = array.reshape(shape.shape())
        except ValueError as err:
            raise CubistError("cannot reshape read data: {t}: {e} [input size={ic}, shape={s}, shape size={sc}]".format(
                    t=type(err).__name__,
                    e=err,
                    ic=array.size,
                    s=shape,
                    sc=shape.count(),
            ))
        return cube

    def write(self, cube, output_format, output_filename):
        numpy_function = None
        numpy_function_pargs = []
        numpy_function_nargs = {}
        output_filename = self.format_filename(output_filename, cube.shape, output_format)
        if output_format == self.FILE_FORMAT_RAW:
            num_bytes = cube.size * self.dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
            numpy_function = cube.tofile
            numpy_function_pargs.append(output_filename)
        elif output_format == self.FILE_FORMAT_CSV:
            msg_bytes = ''
            numpy_function = cube.tofile
            numpy_function_nargs['sep'] = self.output_csv_separator
            numpy_function_pargs.append(output_filename)
        elif output_format == self.FILE_FORMAT_TEXT:
            msg_bytes = ''
            numpy_function = np.savetxt
            numpy_function_pargs.append(output_filename)
            numpy_function_pargs.append(cube)
        else:
            raise CubistError("invalid file format {0!r}".format(output_format))
        self.logger.info("writing {c} {t!r} elements {b}to {f!r} file {o!r}...".format(
            c=cube.size,
            t=self.data_type,
            b=msg_bytes,
            f=output_format,
            o=output_filename))
        numpy_function(*numpy_function_pargs, **numpy_function_nargs)


    def print_cube(self, cube):
        log.PRINT(cube)

    def stat(self, cube):
        cube_sum = cube.sum()
        cube_ave = None
        cobe_count = 0
        if cube.shape != 0:
            cube_count = 1
            for d in cube.shape:
                cube_count *= d
        else:
            cube_count = 0
        if cube_count:
            cube_ave = cube_sum / float(cube_count)
        else:
            cube_ave = None
        cube_count_nonzero = np.count_nonzero(cube)
        cube_count_zero = cube_count - cube_count_nonzero
        cube_fraction_nonzero = 0.0
        if cube_count:
            cube_fraction_nonzero = cube_count_nonzero / float(cube_count)
        cube_fraction_zero = 0.0
        if cube_count:
            cube_fraction_zero = cube_count_zero / float(cube_count)
        stat = """\
shape         = {shape}
#elements     = {count}
min           = {min}
max           = {max}
sum           = {sum}
ave           = {ave}
#zero         = {count_zero} [{fraction_zero:.2%}]
#nonzero      = {count_nonzero} [{fraction_nonzero:.2%}]
""".format(
            shape='x'.join(str(i) for i in cube.shape),
            count=cube_count,
            min=cube.min(),
            max=cube.max(),
            sum=cube_sum,
            ave=cube_ave,
            count_zero=cube_count_zero,
            fraction_zero=cube_fraction_zero,
            count_nonzero=cube_count_nonzero,
            fraction_nonzero=cube_fraction_nonzero,
        )
        log.PRINT(stat)

    def create(self, shape, creation_mode):
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        if creation_mode == self.CREATION_MODE_RANGE:
            cube = np.array(np.linspace(0, shape.count() - 1, shape.count()), dtype=self.dtype)
        elif creation_mode == self.CREATION_MODE_RANDOM:
            cube = np.random.rand(shape.count())
        elif creation_mode == self.CREATION_MODE_ZEROS:
            cube = np.random.zeros(shape.count())
        elif creation_mode == self.CREATION_MODE_ONES:
            cube = np.random.ones(shape.count())
        else:
            raise CubistError("invalid creation mode {0}".format(creation_mode))
        cube = cube.reshape(shape.shape())
        return cube

    def _check_input_filename(self, shape, input_format, input_filename):
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        if not os.path.isfile(input_filename):
            raise CubistError("missing input file {0}".format(input_filename))
        if input_format == self.FILE_FORMAT_RAW:
            expected_input_count = shape.count()
            expected_input_bytes = expected_input_count * self.dtype_bytes
            input_stat_result = os.stat(input_filename)
            input_bytes = input_stat_result.st_size
            if input_bytes < expected_input_bytes:
                raise CubistError("input file {0} is not big enough: it contains {1} bytes, expected {2} bytes".format(
                    input_filename,
                    input_bytes,
                    expected_input_bytes,
                ))
            elif input_bytes > expected_input_bytes:
                message = "input file {0} is greater than expected: {1} bytes found, {2} bytes expected".format(
                    input_filename,
                    input_bytes,
                    expected_input_bytes,
                )
                if self.accept_bigger_raw_files:
                    self.logger.warning("warning: " + message)
                else:
                    raise CubistError(message)
        return input_filename

    def extract(self, cube, selection):
        assert isinstance(selection, Selection)
        if selection.rank() != len(cube.shape):
            raise CubistError("invalid selection {selection} for shape {shape}: rank {rselection} does not match {rshape}".format(
                selection=selection,
                rselection=selection.rank(),
                shape=shape,
                rshape=shape.rank(),
            ))
        subcube = cube[selection.picks()]
        return subcube
 
        
