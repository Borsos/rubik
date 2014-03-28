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

import os
import numpy as np
import warnings
import itertools
from collections import OrderedDict

from . import log
from . import utils
from ..py23 import irange
from ..units import Memory
from ..errors import RubikError, RubikMemoryError
from ..shape import Shape
from ..filename import InputFilename, OutputFilename
from ..application.argdict import InputArgDict, OutputArgDict
from ..application.arglist import ArgList
from ..application.logo import RUBIK
from ..extractor import Extractor
from .. import conf
from .. import cubes

class Rubik(object):
    def __init__(self):
        self.input_filenames = InputArgDict(InputFilename)
        self.input_dtypes = InputArgDict(conf.get_dtype, default=None)
        self.input_formats = InputArgDict(str, default=conf.DEFAULT_FILE_FORMAT)
        self.input_csv_separators = InputArgDict(str, default=conf.FILE_FORMAT_CSV_SEPARATOR)
        self.input_text_delimiters = InputArgDict(str, default=conf.FILE_FORMAT_TEXT_DELIMITER)
        self.shapes = InputArgDict(Shape)
        self.extractors = InputArgDict(Extractor, default=None)

        self.output_filenames = OutputArgDict(OutputFilename)
        self.output_dtypes = OutputArgDict(conf.get_dtype, default=None)
        self.output_formats = OutputArgDict(str, default=conf.DEFAULT_FILE_FORMAT)
        self.output_csv_separators = OutputArgDict(str, default=conf.FILE_FORMAT_CSV_SEPARATOR)
        self.output_text_delimiters = OutputArgDict(str, default=conf.FILE_FORMAT_TEXT_DELIMITER)
        self.output_text_newlines = OutputArgDict(str, default=conf.FILE_FORMAT_TEXT_NEWLINE)
        self.output_text_converters = OutputArgDict(str, default=conf.FILE_FORMAT_TEXT_CONVERTER)

        self.expressions = ArgList(str)

        default_dtype = conf.get_dtype(conf.DEFAULT_DATA_TYPE)
        self.logger = log.LOGGER

        self.set_accept_bigger_raw_files(False)
        self.set_read_mode(conf.DEFAULT_READ_MODE)
        self.set_optimized_min_size(conf.DEFAULT_OPTIMIZED_MIN_SIZE)
        self.set_memory_limit(conf.DEFAULT_LIMIT_MEMORY)
        self.set_split_dimensions(None)
        self.set_clobber(conf.DEFAULT_CLOBBER)
        self.set_print_cube(False)
        self.set_print_stats(False)
        self.set_in_place(False)
        self.set_dtype(default_dtype)

        self.total_read_bytes = 0
        self.input_cubes = OrderedDict()

        self._used_input_filenames = set()
        self._used_output_filenames = set()

        self._result = None
        self._locals = {}

    def show_logo(self):
        log.PRINT(RUBIK)

    def show_logo_once(self):
        attr_name = '_logo_has_been_shown'
        if not getattr(self, attr_name, False):
            self.show_logo()
            setattr(self, attr_name, True)

    def set_dtype(self, dtype):
        self.dtype = dtype
        cubes.set_default_dtype(self.dtype)
        self.dtype_bytes = self.dtype().itemsize
        self._cache_dtype_bytes = {self.dtype: self.dtype_bytes}

    def set_logger(self, logger):
        self.logger = logger

    def set_accept_bigger_raw_files(self, accept_bigger_raw_files):
        self.accept_bigger_raw_files = accept_bigger_raw_files

    def set_read_mode(self, read_mode):
        self.read_mode = read_mode

    def set_in_place(self, in_place):
        self.in_place = in_place

    def set_optimized_min_size(self, optimized_min_size):
        self.optimized_min_size = optimized_min_size

    def set_memory_limit(self, memory_limit):
        self.memory_limit = memory_limit
        self.memory_limit_bytes = memory_limit.get_bytes()

    def set_split_dimensions(self, split_dimensions):
        if split_dimensions is None:
            split_dimensions = ()
        self.split_dimensions = split_dimensions

    def set_clobber(self, clobber):
        self.clobber = clobber

    def set_print_cube(self, print_cube):
        self.print_cube = print_cube

    def set_print_stats(self, print_stats):
        self.print_stats = print_stats

    def run(self):
        self.read()
        if self.expressions:
            self.evaluate_expressions(*self.expressions)
        else:
            if self.input_filenames is None or len(self.input_filenames) == 0:
                #self.show_logo_once()
                self.logger.warning("warning: nothing to do; you should use at least one option between '--input-filename/-i', '--expression/-e'")
                return
            elif len(self.input_filenames) == 0:
                self.logger.warning("warning: loading more than an input file is useless if '--expression/-e' is not used")

        if self.in_place:
            if self.output_filenames:
                raise RubikError("--in-place/-Oi is not compatible with --output-filename/-o")
            else:
                for input_filename in self.input_filenames.values():
                    self.output_filenames.add(input_filename.filename())
        #print "I", InputFilename.__filenames__
        #print "O", OutputFilename.__filenames__
        self.output()

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

    def result(self):
        return self._result

    def read(self):
        self._result = None
        if not self.input_filenames:
            return
        for input_label, input_filename in self.input_filenames.items():
            self._result = self._read(input_label, input_filename)

    def _check_memory_limit(self, input_label, input_filename):
        input_ordinal = self.input_filenames.get_ordinal(input_label)
        shape = self.shapes.get(input_label, input_ordinal)
        if shape is None:
            raise RubikError("missing shape for filename {0}".format(input_filename))
        extractor = self.extractors.get(input_label, input_ordinal)
        if extractor is not None:
            count, sub_count = extractor.get_counts(shape)
        else:
            count = shape.count()
            sub_count = count
        input_dtype = self.input_dtypes.get(input_label, input_ordinal)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        input_bytes_sub = sub_count * input_dtype_bytes 
        if self.read_mode is conf.READ_MODE_OPTIMIZED:
            input_bytes_read = input_bytes_sub
        else:
            input_bytes_read = count * input_dtype_bytes 
        self.logger.debug("trying to read {0} bytes and extract {1} bytes; already read {2} bytes...".format(
                    input_bytes_read,
                    input_bytes_sub,
                    self.total_read_bytes))
        if self.memory_limit_bytes > 0 and self.total_read_bytes + input_bytes_read > self.memory_limit_bytes:
            raise RubikMemoryError("trying to read {0} + {1} = {2} bytes, more than memory limit {1}".format(
                    self.total_read_bytes,
                    input_bytes_read,
                    self.total_read_bytes + input_bytes_read,
                    self.memory_limit))
        self.total_read_bytes += input_bytes_sub

    def _read(self, input_label, input_filename):
        self._check_memory_limit(input_label, input_filename)
        if self.read_mode == conf.READ_MODE_SAFE:
            return self._read_safe(input_label, input_filename)
        elif self.read_mode == conf.READ_MODE_OPTIMIZED:
            return self._read_optimized(input_label, input_filename)
        else:
            raise RubikError("invalid read mode {0!r}".format(self.read_mode))

    def _read_safe(self, input_label, input_filename):
        self.logger.debug("executing safe read...")
        input_ordinal = self.input_filenames.get_ordinal(input_label)
        shape = self.shapes.get(input_label, input_ordinal)
        if shape is None:
            raise RubikError("missing shape for filename {0}".format(input_filename))
        input_format = self.input_formats.get(input_label, input_ordinal)
        if input_format is None:
            input_format = conf.DEFAULT_FILE_FORMAT
        input_dtype = self.input_dtypes.get(input_label, input_ordinal)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        extractor = self.extractors.get(input_label, input_ordinal)
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
            numpy_function_nargs['sep'] = self.input_csv_separators.get(input_label, input_ordinal)
        elif input_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            # read all elements (must check number of elements)
            numpy_function = np.loadtxt
            text_delimiter = self.input_text_delimiters.get(input_label, input_ordinal)
            if text_delimiter is not None:
                numpy_function_nargs['delimiter'] = text_delimiter
        else:
            raise RubikError("invalid file format {0!r}".format(input_format))
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
                raise RubikError("input file {0} is not big enough: it contains {1} elements, expected {2} elements".format(
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
                    warnings.warn(RuntimeWarning(message))
                    #self.logger.warning("warning: " + message)
                else:
                    raise RubikError(message)
                array.resize(shape.shape())
        try:
            cube = array.reshape(shape.shape())
        except ValueError as err:
            raise RubikError("cannot reshape read data: {t}: {e} [input size={ic}, shape={s}, shape size={sc}]".format(
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
        input_ordinal = self.input_filenames.get_ordinal(input_label)
        shape = self.shapes.get(input_label, input_ordinal)
        if shape is None:
            raise RubikError("missing shape for filename {0}".format(input_filename))
        input_format = self.input_formats.get(input_label, input_ordinal)
        if input_format is None:
            input_format = conf.DEFAULT_FILE_FORMAT
        input_dtype = self.input_dtypes.get(input_label, input_ordinal)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        extractor = self.extractors.get(input_label, input_ordinal)
        assert isinstance(input_filename, InputFilename)
        assert (extractor is None) or isinstance(extractor, Extractor)
        input_filename = input_filename.filename
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        if extractor:
            expected_input_count, expected_read_count = extractor.get_counts(shape)
        else:
            expected_input_count = shape.count()
            expected_read_count = expected_input_count
        numpy_function = cubes.fromfile_generic
        numpy_function_nargs = {}
        numpy_function_pargs = []
        if input_format == conf.FILE_FORMAT_RAW:
            num_bytes = expected_read_count * input_dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
        elif input_format == conf.FILE_FORMAT_CSV:
            msg_bytes = ''
            numpy_function_nargs['sep'] = self.input_csv_separators.get(input_label, input_ordinal)
        elif input_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            text_delimiter = self.input_text_delimiters.get(input_label, input_ordinal)
            if text_delimiter is not None:
                numpy_function_nargs['delimiter'] = text_delimiter
        else:
            raise RubikError("invalid file format {0!r}".format(input_format))
        input_filename = self.format_filename(input_filename, shape.shape(), input_format, input_dtype)
        input_filename = self._check_input_filename(shape, input_format, input_filename, input_dtype)
        if extractor is None:
            extractor_msg = ''
        else:
            extractor_msg = "[{0}]".format(extractor)
        self.logger.info("reading {c} {t!r} elements {b}from {f!r} file {i!r}{x}...".format(
            c=expected_read_count,
            t=input_dtype.__name__,
            b=msg_bytes,
            f=input_format,
            i=input_filename,
            x=extractor_msg))
        cube = numpy_function(input_format, input_filename, shape=shape, extractor=extractor, dtype=input_dtype, min_size=self.optimized_min_size, *numpy_function_pargs, **numpy_function_nargs)
        self.register_input_cube(input_label, input_filename, cube)
        return cube

    def split_over_dimensions(self, cube):
        if self.split_dimensions:
            l = []
            for dimension in self.split_dimensions:
                if 0 <= dimension < len(cube.shape):
                    l.append([(dimension, i) for i in irange(cube.shape[dimension])])
            get_all = slice(None, None, None)
            for d_indices in itertools.product(*l):
                dd = dict(d_indices)
                ex = []
                for d in irange(len(cube.shape)):
                    ex.append(dd.get(d, get_all))
                dlabels = OrderedDict(('d{0}'.format(i), j) for i, j in d_indices)
                subcube = cube[tuple(ex)]
                yield subcube, dlabels
        else:
            yield cube, None
        
    def output(self):
        useless_run = True
        cube = self._result
        for subcube, dlabels in self.split_over_dimensions(cube):
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
                self._write_cube(cube=subcube, dlabels=dlabels)
        if useless_run:
            #self.show_logo_once()
            #self.logger.warning("warning: nothing to do; you should at least one of these options: --print/-P, --stats/-S, --output-filename/-o")
            pass
    
    def write(self, cube):
        if not self.output_filenames:
            return
        for subcube, dlabels in self.split_over_dimensions(cube):
            self._write_cube(subcube, dlabels)

    def _write_cube(self, cube, dlabels=None):
        #if not isinstance(cube, np.ndarray):
        #    raise RubikError("cannot write result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
        for output_label, output_filename in self.output_filenames.items():
            self._write(cube, output_label, output_filename, dlabels=dlabels)
        
    def _write(self, cube, output_label, output_filename, dlabels=None):
        output_ordinal = self.output_filenames.get_ordinal(output_label)
        output_format = self.output_formats.get(output_label, output_ordinal)
        if output_format is None:
            output_format = conf.DEFAULT_FILE_FORMAT
        output_dtype = self.output_dtypes.get(output_label, output_ordinal)
        if output_dtype is None:
            output_dtype = self.dtype
        output_dtype_bytes = self.get_dtype_bytes(output_dtype)
        if cube.dtype != output_dtype:
            cube = cube.astype(output_dtype)
        assert isinstance(output_filename, OutputFilename), (output_filename, type(output_filename))
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
            numpy_function_nargs['sep'] = self.output_csv_separators.get(output_label, output_ordinal)
            numpy_function_pargs.append(output_filename)
        elif output_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            numpy_function = np.savetxt
            numpy_function_pargs.append(output_filename)
            if len(cube.shape) <= 2:
                c2d = cube
            else:
                c2d = cube.reshape((cube.shape[0], cube.size / cube.shape[0]))
            numpy_function_pargs.append(c2d)
            text_delimiter = self.output_text_delimiters.get(output_label, output_ordinal)
            text_newline = self.output_text_newlines.get(output_label, output_ordinal)
            text_converter = self.output_text_converters.get(output_label, output_ordinal)
            if text_delimiter is not None:
                numpy_function_nargs['delimiter'] = text_delimiter
            if text_newline is not None:
                numpy_function_nargs['newline'] = text_newline
            if text_converter is not None:
                numpy_function_nargs['fmt'] = text_convert
        else:
            raise RubikError("invalid file format {0!r}".format(output_format))
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
            raise RubikError("cannot stat result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
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
            raise RubikError("output file {0!r} already exists".format(output_filename))
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
            raise RubikError("missing input file {0}".format(input_filename))
        if input_format == conf.FILE_FORMAT_RAW:
            expected_input_count = shape.count()
            expected_input_bytes = expected_input_count * self.get_dtype_bytes(input_dtype)
            input_stat_result = os.stat(input_filename)
            input_bytes = input_stat_result.st_size
            if input_bytes < expected_input_bytes:
                raise RubikError("input file {0} is not big enough: it contains {1} bytes, expected {2} bytes".format(
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
                    warnings.warn(RuntimeWarning(message))
                    #self.logger.warning("warning: " + message)
                else:
                    raise RubikError(message)
        return input_filename

    def extract(self, cube, extractor):
        assert isinstance(extractor, Extractor)
        if extractor.rank() != len(cube.shape):
            raise RubikError("invalid extractor {extractor} for shape {shape}: rank {rextractor} does not match {rshape}".format(
                extractor=extractor,
                rextractor=extractor.rank(),
                shape=cube.shape,
                rshape=len(cube.shape),
            ))
        self.logger.info("extracting '{0}'...".format(extractor))
        subcube = cube[extractor.index_pickers()]
        return subcube
 
    def evaluate_expressions(self, *expressions):
        globals_d = {
            'np': np,
            'numpy': np,
            'cb': cubes,
            'cubes': cubes,
        }
        globals_d.update(self.input_cubes)
        locals_d = {
            '_r': self._result,
        }
        result = self._result
        for expression in expressions:
            if expression.startswith('@'):
                source_filename = expression[1:]
                self.logger.info("loading source from file {0!r}...".format(source_filename))
                if not os.path.exists(source_filename):
                    raise RubikError("cannot compile expression {0!r}: missing filename {1}".format(expression, source_filename))
                try:
                    with open(source_filename, "r") as f_in:
                        source = f_in.read()
                except Exception as err:
                    raise RubikError("cannot load source from file {0}: {1}: {2}".format(source_filename, type(err).__name__, err))
                try:
                    mode = 'exec'
                    compiled_expression = compile(source, source_filename, mode)
                except SyntaxError as err:
                    raise RubikError("cannot compile expression {0!r}: {1}: {2}".format(expression, type(err).__name__, err))
            else:
                self.logger.info("evaluating expression {0!r}...".format(expression))
                try:
                    mode = 'eval'
                    compiled_expression = compile(expression, '<string>', mode)
                except SyntaxError as err:
                    try:
                        mode = 'exec'
                        compiled_expression = compile(expression, '<string>', mode)
                    except SyntaxError as err:
                        raise RubikError("cannot compile expression {0!r}: {1}: {2}".format(expression, type(err).__name__, err))
            try:
                self.logger.debug("executing {0!r} expression...".format(mode))
                result = eval(compiled_expression, globals_d, locals_d)
                if mode == 'eval':
                    self._result = result
                    locals_d['_r'] = self._result
                else:
                    self._result = locals_d.get('_r', None)
            except Exception as err:
                raise RubikError("cannot evaluate expression {0!r}: {1}: {2}".format(expression, type(err).__name__, err))
            #if result.dtype != self.dtype:
            #    result = result.astype(self.dtype)
        
