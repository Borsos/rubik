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
from .errors import SubCubeError
from .origins import Origins
from .shape import Shape
from .selection import Selection

class Cube(object):
    CREATION_MODE_RANDOM = 'random'
    CREATION_MODE_RANGE = 'range'
    CREATION_MODE_ZEROS = 'zeros'
    CREATION_MODE_ONES = 'ones'
    CREATION_MODES = (CREATION_MODE_RANDOM, CREATION_MODE_RANGE, CREATION_MODE_ZEROS, CREATION_MODE_ONES)
    def __init__(self, origins, shape, data_type, logger):
        assert isinstance(origins, Origins)
        assert isinstance(shape, Shape)
        if origins.rank() != shape.rank():
            raise SubCubeError("invalid origins {origins} for shape {shape}: rank {rorigins} does not match {rshape}".format(
                origins=origins,
                rorigins=origins.rank(),
                shape=shape,
                rshape=shape.rank(),
            ))
        self.shape = shape
        self.origins = origins
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

    def print(self, input_filename):
        expected_input_count, expected_input_size, input_filename = self._check_input_filename(input_filename)
        with open(input_filename, "rb") as input_file:
            self.logger.info("reading {c} {t!r} elements ({b} bytes) from {i}...".format(
                c=expected_input_count,
                t=self.data_type,
                b=expected_input_size,
                i=input_filename))
            array = np.fromfile(input_file, dtype=self.dtype, count=expected_input_count)
            cube = array.reshape(self.shape.shape())
            log.PRINT(cube)

    def create(self, output_filename, creation_mode):
        if creation_mode == self.CREATION_MODE_RANGE:
            cube = np.array(np.linspace(0, self.shape.count() - 1, self.shape.count()), dtype=self.dtype)
        elif creation_mode == self.CREATION_MODE_RANDOM:
            cube = np.random.rand(self.shape.count())
        elif creation_mode == self.CREATION_MODE_ZEROS:
            cube = np.random.zeros(self.shape.count())
        elif creation_mode == self.CREATION_MODE_ONES:
            cube = np.random.ones(self.shape.count())
        else:
            raise SubCubeError("invalid creation mode {0}".format(creation_mode))
        cube = cube.reshape(self.shape.shape())
        output_filename = self.format_filename(output_filename, cube.shape)
        with open(output_filename, "wb") as output_file:
            cube.tofile(output_file)

    def _check_input_filename(self, input_filename):
        input_filename = self.format_filename(input_filename, self.shape.shape())
        if not os.path.isfile(input_filename):
            raise SubCubeError("missing input file {0}".format(input_filename))
        input_stat_result = os.stat(input_filename)
        input_size = input_stat_result.st_size
        expected_input_count = self.shape.count()
        expected_input_size = expected_input_count * self.dtype_size
        if input_size < expected_input_size:
            raise SubCubeError("input file {0} is not big enough: it contains {1} bytes, expected {2} bytes".format(
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

    def extract(self, selection, input_filename, output_filename):
        assert isinstance(selection, Selection)
        if selection.rank() != self.shape.rank():
            raise SubCubeError("invalid selection {selection} for shape {shape}: rank {rselection} does not match {rshape}".format(
                selection=selection,
                rselection=selection.rank(),
                shape=shape,
                rshape=shape.rank(),
            ))
        expected_input_count, expected_input_size, input_filename = self._check_input_filename(input_filename)
        with open(input_filename, "rb") as input_file:
            self.logger.info("reading {c} {t!r} elements ({b} bytes) from {i}...".format(
                c=expected_input_count,
                t=self.data_type,
                b=expected_input_size,
                i=input_filename))
            array = np.fromfile(input_file, dtype=self.dtype, count=expected_input_count)
            cube = array.reshape(self.shape.shape())
            subcube = cube[selection.picks(self.origins)]
            output_filename = self.format_filename(output_filename, subcube.shape)
            self.logger.info("writing {c} {t!r} elements ({b} bytes) to {o}...".format(
                c=subcube.size,
                t=self.data_type,
                b=subcube.size * self.dtype_size,
                o=output_filename))
            with open(output_filename, "wb") as output_file:
                subcube.tofile(output_file)
 
        
