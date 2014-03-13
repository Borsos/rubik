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
    def __init__(self, data_type, logger):
        self.data_type = data_type
        self.dtype = data_types.get_dtype(data_type)
        self.dtype_size = self.dtype().itemsize
        self.logger = logger

    def format_filename(self, filename, shape):
        count = 0
        if shape:
            count = 1
            for i in shape:
                count *= i
        else:
            count = 0
        num_bytes = count * self.dtype_size
        return filename.format(
            shape="x".join(str(i) for i in shape),
            count=count,
            bytes=num_bytes,
            data_type=self.data_type,
        )

    def read(self, shape, input_filename):
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        expected_input_count, expected_input_size, input_filename = self._check_input_filename(shape, input_filename)
        with open(input_filename, "rb") as input_file:
            self.logger.info("reading {c} {t!r} elements ({b} bytes) from {i}...".format(
                c=expected_input_count,
                t=self.data_type,
                b=expected_input_size,
                i=input_filename))
            array = np.fromfile(input_file, dtype=self.dtype, count=expected_input_count)
        cube = array.reshape(shape.shape())
        return cube

    def write(self, cube, output_filename):
        output_filename = self.format_filename(output_filename, cube.shape)
        self.logger.info("writing {c} {t!r} elements ({b} bytes) to {o}...".format(
            c=cube.size,
            t=self.data_type,
            b=cube.size * self.dtype_size,
            o=output_filename))
        with open(output_filename, "wb") as output_file:
            cube.tofile(output_file)

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

    def _check_input_filename(self, shape, input_filename):
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        input_filename = self.format_filename(input_filename, shape.shape())
        if not os.path.isfile(input_filename):
            raise CubistError("missing input file {0}".format(input_filename))
        input_stat_result = os.stat(input_filename)
        input_size = input_stat_result.st_size
        expected_input_count = shape.count()
        expected_input_size = expected_input_count * self.dtype_size
        if input_size < expected_input_size:
            raise CubistError("input file {0} is not big enough: it contains {1} bytes, expected {2} bytes".format(
                input_filename,
                input_size,
                expected_input_size,
            ))
        elif input_size > expected_input_size:
            self.logger.warning("warning: input file {0} is greater than expected: {1} bytes found, {2} bytes expected".format(
                input_filename,
                input_size,
                expected_input_size,
            ))
        return expected_input_count, expected_input_size, input_filename

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
 
        
