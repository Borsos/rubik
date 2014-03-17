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
import itertools
from collections import OrderedDict

from .application import log
from .errors import CubistError
from .clip import Clip
from .shape import Shape
from .filename import InputFilename, OutputFilename
from .variable import VariableDefinition
from .extractor import Extractor
from . import conf
from . import cubist_numpy

class Cubist(object):
    def __init__(self,
            dtype,
            logger,
            input_filenames,
            input_formats,
            input_dtypes,
            output_filenames,
            output_dtypes,
            output_formats,
            extractors,
            shapes,
            input_csv_separators,
            output_csv_separators,
            input_text_delimiters,
            output_text_delimiters,
            output_text_newlines,
            output_text_converters,
            accept_bigger_raw_files=False,
            read_mode=conf.DEFAULT_READ_MODE,
            loop_dimensions=None,
            clobber=conf.DEFAULT_CLOBBER,
            print_cube=False,
            print_stats=False):
        self._set_dtype(dtype)
        self.logger = logger
        self.input_csv_separators = input_csv_separators
        self.output_csv_separators = output_csv_separators
        self.input_text_delimiters = input_text_delimiters
        self.output_text_delimiters = output_text_delimiters
        self.output_text_newlines = output_text_newlines
        self.output_text_converters = output_text_converters
        self.accept_bigger_raw_files = accept_bigger_raw_files
        self.read_mode = read_mode
        if read_mode == conf.READ_MODE_SAFE:
            self._read = self._read_safe
        elif self.read_mode == conf.READ_MODE_OPTIMIZED:
            self._read = self._read_optimized
        else:
            raise CubistError("invalid read mode {0!r}".format(read_mode))

        self.clobber = clobber

        self.print_cube = print_cube
        self.print_stats = print_stats

        if loop_dimensions is None:
            loop_dimensions = ()
        self.loop_dimensions = loop_dimensions

        self._last_cube = None
        self.input_cubes = OrderedDict()

        self.input_filenames = input_filenames
        self.input_formats = input_formats
        self.input_dtypes = input_dtypes
        self.shapes = shapes
        self.extractors = extractors

        self.output_filenames = output_filenames
        self.output_dtypes = output_dtypes
        self.output_formats = output_formats

        self._used_input_filenames = set()
        self._used_output_filenames = set()

    def _set_dtype(self, dtype):
        self.dtype = dtype
        cubist_numpy.set_default_dtype(self.dtype)
        self.dtype_bytes = self.dtype().itemsize
        self._cache_dtype_bytes = {self.dtype: self.dtype_bytes}

    def get_dtype_bytes(self, dtype):
        if not dtype in self._cache_dtype_bytes:
            self._cache_dtype_bytes[dtype] = dtype().itemsize
        return self._cache_dtype_bytes[dtype]

    def format_filename(self, filename, shape, file_format, file_dtype, dlabels=None):
        if dlabels is None:
            dlabels = {}
        count = 0
        if shape:
            count = 1
            for i in shape:
                count *= i
        else:
            count = 0
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        return filename.format(
            shape=shape, #"x".join(str(i) for i in shape),
            rank=len(shape),
            count=count,
            format=file_format,
            dtype=file_dtype.__name__,
            **dlabels
        )

    def register_input_cube(self, input_label, input_filename, cube):
        self.input_cubes[input_label] = cube

    def last_cube(self):
        return self._last_cube

    def read(self):
        self._last_cube = None
        if not self.input_filenames:
            return
        for input_label, input_filename in self.input_filenames.items():
            self._last_cube = self._read(input_label, input_filename)

    def _read_safe(self, input_label, input_filename):
        self.logger.debug("executing safe read...")
        shape = self.shapes.get(input_label)
        if shape is None:
            raise CubistError("missing shape for filename {0}".format(input_filename))
        input_format = self.input_formats.get(input_label)
        if input_format is None:
            input_format = conf.DEFAULT_FILE_FORMAT
        input_dtype = self.input_dtypes.get(input_label)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        extractor = self.extractors.get(input_label)
        assert isinstance(input_filename, InputFilename)
        assert (extractor is None) or isinstance(extractor, Extractor)
        input_filename = input_filename.filename
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        expected_input_count = shape.count()
        numpy_function = None
        numpy_function_nargs = {}
        numpy_function_pargs = []
        if input_format == conf.FILE_FORMAT_RAW:
            num_bytes = shape.count() * input_dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
            # read only expected elements (number of elements already checked)
            numpy_function = np.fromfile
            numpy_function_nargs['count'] = expected_input_count
        elif input_format == conf.FILE_FORMAT_CSV:
            msg_bytes = ''
            # read all elements (must check number of elements)
            numpy_function = np.fromfile
            numpy_function_nargs['sep'] = self.input_csv_separators.get(input_label)
        elif input_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            # read all elements (must check number of elements)
            numpy_function = np.loadtxt
            text_delimiter = self.input_text_delimiters.get(input_label)
            if text_delimiter is not None:
                numpy_function_nargs['delimiter'] = text_delimiter
        else:
            raise CubistError("invalid file format {0!r}".format(input_format))
        input_filename = self.format_filename(input_filename, shape.shape(), input_format, input_dtype)
        input_filename = self._check_input_filename(shape, input_format, input_filename, input_dtype)
        self.logger.info("reading {c} {t!r} elements {b}from {f!r} file {i!r}...".format(
            c=expected_input_count,
            t=input_dtype.__name__,
            b=msg_bytes,
            f=input_format,
            i=input_filename))
        array = numpy_function(input_filename, dtype=input_dtype, *numpy_function_pargs, **numpy_function_nargs)
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
        if extractor:
            cube = self.extract(cube, extractor)
        self.register_input_cube(input_label, input_filename, cube)
        return cube

    def _read_optimized(self, input_label, input_filename):
        self.logger.debug("executing optimized read...")
        shape = self.shapes.get(input_label)
        if shape is None:
            raise CubistError("missing shape for filename {0}".format(input_filename))
        input_format = self.input_formats.get(input_label)
        if input_format is None:
            input_format = conf.DEFAULT_FILE_FORMAT
        input_dtype = self.input_dtypes.get(input_label)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        extractor = self.extractors.get(input_label)
        assert isinstance(input_filename, InputFilename)
        assert (extractor is None) or isinstance(extractor, Extractor)
        input_filename = input_filename.filename
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        expected_input_count = shape.count()
        numpy_function = cubist_numpy.fromfile_generic
        numpy_function_nargs = {}
        numpy_function_pargs = []
        if input_format == conf.FILE_FORMAT_RAW:
            num_bytes = shape.count() * input_dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
        elif input_format == conf.FILE_FORMAT_CSV:
            msg_bytes = ''
            numpy_function_nargs['sep'] = self.input_csv_separators.get(input_label)
        elif input_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            text_delimiter = self.input_text_delimiters.get(input_label)
            if text_delimiter is not None:
                numpy_function_nargs['delimiter'] = text_delimiter
        else:
            raise CubistError("invalid file format {0!r}".format(input_format))
        input_filename = self.format_filename(input_filename, shape.shape(), input_format, input_dtype)
        input_filename = self._check_input_filename(shape, input_format, input_filename, input_dtype)
        self.logger.info("reading {c} {t!r} elements {b}from {f!r} file {i!r}...".format(
            c=expected_input_count,
            t=input_dtype.__name__,
            b=msg_bytes,
            f=input_format,
            i=input_filename))
        cube = numpy_function(input_format, input_filename, shape=shape, extractor=extractor, dtype=input_dtype, *numpy_function_pargs, **numpy_function_nargs)
        self.register_input_cube(input_label, input_filename, cube)
        return cube

    def loop_over_dimensions(self, cube):
        if self.loop_dimensions:
            l = []
            for dimension in self.loop_dimensions:
                if 0 <= dimension < cube.shape:
                    l.append([(dimension, i) for i in range(cube.shape[dimension])])
            get_all = slice(None, None, None)
            for d_indices in itertools.product(*l):
                dd = dict(d_indices)
                ex = []
                for d in range(len(cube.shape)):
                    ex.append(dd.get(d, get_all))
                dlabels = OrderedDict(('d{0}'.format(i), j) for i, j in d_indices)
                #print dlabels, ex
                subcube = cube[tuple(ex)]
                yield subcube, dlabels
        else:
            yield cube, None
        
    def output(self, cube):
        useless_run = True
        for subcube, dlabels in self.loop_over_dimensions(cube):
            if self.print_cube or self.print_stats:
                self._log_dlabels(dlabels)
            if self.print_cube:
                self._print_cube(cube=subcube)
                useless_run = False
            if self.print_stats:
                self._print_stats(cube=subcube)
                useless_run = False
            if self.output_filenames:
                useless_run = False
                self._write_cube(cube=subcube)
        if useless_run:
            self.logger.warning("warning: nothing to do; you should at least one of these options: --print/-P, --stats/-S, --output-filename/-o")
    
    def write(self, cube):
        if not self.output_filenames:
            return
        for subcube, dlabels in self.loop_over_dimensions(cube):
            self._write_cube(subcube, dlabels)

    def _write_cube(self, cube, dlabels=None):
        if not isinstance(cube, np.ndarray):
            raise CubistError("cannot write result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
        for output_label, output_filename in self.output_filenames.items():
            self._write(cube, output_label, output_filename, dlabels=dlabels)
        
    def _write(self, cube, output_label, output_filename, dlabels=None):
        output_format = self.output_formats.get(output_label)
        if output_format is None:
            output_format = conf.DEFAULT_FILE_FORMAT
        output_dtype = self.output_dtypes.get(output_label)
        if output_dtype is None:
            output_dtype = self.dtype
        output_dtype_bytes = self.get_dtype_bytes(output_dtype)
        if cube.dtype != output_dtype:
            cube = cube.astype(output_dtype)
        assert isinstance(output_filename, OutputFilename)
        output_filename = output_filename.filename
        numpy_function = None
        numpy_function_pargs = []
        numpy_function_nargs = {}
        output_filename = self.format_filename(output_filename, cube.shape, output_format, output_dtype, dlabels=dlabels)
        self._check_output_filename(output_filename)
        if output_format == conf.FILE_FORMAT_RAW:
            num_bytes = cube.size * output_dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
            numpy_function = cube.tofile
            numpy_function_pargs.append(output_filename)
        elif output_format == conf.FILE_FORMAT_CSV:
            msg_bytes = ''
            numpy_function = cube.tofile
            numpy_function_nargs['sep'] = self.output_csv_separators.get(output_label)
            numpy_function_pargs.append(output_filename)
        elif output_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            numpy_function = np.savetxt
            numpy_function_pargs.append(output_filename)
            numpy_function_pargs.append(cube)
            text_delimiter = self.output_text_delimiters.get(output_label)
            text_newline = self.output_text_newlines.get(output_label)
            text_converter = self.output_text_converters.get(output_label)
            if text_delimiter is not None:
                numpy_function_nargs['delimiter'] = text_delimiter
            if text_newline is not None:
                numpy_function_nargs['newline'] = text_newline
            if text_converter is not None:
                numpy_function_nargs['fmt'] = text_convert
        else:
            raise CubistError("invalid file format {0!r}".format(output_format))
        self.logger.info("writing {c} {t!r} elements {b}to {f!r} file {o!r}...".format(
            c=cube.size,
            t=output_dtype.__name__,
            b=msg_bytes,
            f=output_format,
            o=output_filename))
        numpy_function(*numpy_function_pargs, **numpy_function_nargs)

    def _log_dlabels(self, dlabels):
        if dlabels:
            dlabels_message = "## " + ', '.join("{0}={1}".format(dlabel, dvalue) for dlabel, dvalue in dlabels.items())
            log.PRINT(dlabels_message)

    def _print_cube(self, cube):
        log.PRINT(cube)

    def _print_stats(self, cube):
        self.stats_cube(cube)

    def stats_cube(self, cube):
        if not isinstance(cube, np.ndarray):
            raise CubistError("cannot stat result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
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
        cube_count_nan = np.count_nonzero(np.isnan(cube))
        if cube_count:
            cube_fraction_nan = cube_count_nan / float(cube_count)
        cube_count_inf = np.count_nonzero(np.isinf(cube))
        if cube_count:
            cube_fraction_inf = cube_count_inf / float(cube_count)
        stat = """\
shape         = {shape}
#elements     = {count}
min           = {min}
max           = {max}
sum           = {sum}
ave           = {ave}
#zero         = {count_zero} [{fraction_zero:.2%}]
#nonzero      = {count_nonzero} [{fraction_nonzero:.2%}]
#nan          = {count_nan} [{fraction_nan:.2%}]
#inf          = {count_inf} [{fraction_inf:.2%}]
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
            count_nan=cube_count_nan,
            fraction_nan=cube_fraction_nan,
            count_inf=cube_count_inf,
            fraction_inf=cube_fraction_inf,
        )
        log.PRINT(stat)

    def _check_output_filename(self, output_filename):
        if (not self.clobber) and os.path.exists(output_filename):
            raise CubistError("output file {0!r} already exists".format(output_filename))
        if output_filename in self._used_output_filenames:
            self.logger.warning("warning: output filename {0!r} already written".format(output_filename))
        self._used_output_filenames.add(output_filename)

    def _check_input_filename(self, shape, input_format, input_filename, input_dtype):
        if input_filename in self._used_input_filenames:
            self.logger.warning("warning: input filename {0!r} already read".format(input_filename))
        self._used_input_filenames.add(input_filename)

        if not isinstance(shape, Shape):
            shape = Shape(shape)
        if not os.path.isfile(input_filename):
            raise CubistError("missing input file {0}".format(input_filename))
        if input_format == conf.FILE_FORMAT_RAW:
            expected_input_count = shape.count()
            expected_input_bytes = expected_input_count * self.get_dtype_bytes(input_dtype)
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

    def extract(self, cube, extractor):
        assert isinstance(extractor, Extractor)
        if extractor.rank() != len(cube.shape):
            raise CubistError("invalid extractor {extractor} for shape {shape}: rank {rextractor} does not match {rshape}".format(
                extractor=extractor,
                rextractor=extractor.rank(),
                shape=cube.shape,
                rshape=len(cube.shape),
            ))
        self.logger.info("extracting '{0}'...".format(extractor))
        subcube = cube[extractor.index_pickers()]
        return subcube
 
    def evaluate_expression(self, expression):
        globals_d = {
            'np': np,
            'numpy': np,
            'cnp': cubist_numpy,
            'cubist_numpy': cubist_numpy,
        }
        globals_d.update(self.input_cubes)
        locals_d = {}
        for var_name, var_instance in VariableDefinition.__variables__.items():
            var_instance.evaluate(globals_d)
            locals_d[var_name] = var_instance.value()
        self.logger.info("evaluating expression {0!r}...".format(expression))
        try:
            result = eval(expression, globals_d, locals_d)
        except Exception as e:
            raise CubistError("cannot evaluate expression {0!r}: {1}: {2}".format(expression, type(e).__name__, e))
        #if result.dtype != self.dtype:
        #    result = result.astype(self.dtype)
        return result
        
