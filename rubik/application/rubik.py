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
import logging
import warnings
import itertools
from collections import OrderedDict

from . import log
from . import utils
from . import config
from ..py23 import irange
from ..units import Memory
from ..errors import RubikError, RubikMemoryError
from ..shape import Shape
from ..filename import InputFilename, OutputFilename, InputMode, OutputMode
from ..application.argdict import ResultArgDict, InputArgDict, OutputArgDict
from ..application.arglist import ArgList
from ..application.logo import RUBIK
from ..extractor import Extractor
from ..format_filename import format_filename
from ..visualizer.controller_builder import controller_builder
from ..visualizer.visualizer_builder import visualizer_builder
from .. import conf
from ..cubes import internals as cubes_internals
from ..cubes import api as cubes_api

class Rubik(object):
    def __init__(self):
        self.name = "{} {}".format(self.__class__.__name__, conf.VERSION)
        self._log_header = "{}: ".format(self.__class__.__name__.lower())
        self.config = config.get_config()

        self.input_filenames = InputArgDict(InputFilename)
        self.input_modes = InputArgDict(InputMode, default=InputMode("rb"))
        self.input_offsets = InputArgDict(Memory, default=None)
        self.input_dtypes = InputArgDict(conf.get_dtype, default=None)
        self.input_formats = InputArgDict(str, default=self.config.default_file_format)
        self.input_csv_separators = InputArgDict(str, default=conf.FILE_FORMAT_CSV_SEPARATOR)
        self.input_text_delimiters = InputArgDict(str, default=conf.FILE_FORMAT_TEXT_DELIMITER)
        self.shapes = InputArgDict(Shape)
        self.extractors = InputArgDict(Extractor, default=None)

        self.output_filenames = OutputArgDict(OutputFilename)
        self.output_modes = OutputArgDict(OutputMode)
        self.output_offsets = OutputArgDict(Memory, default=None)
        self.output_dtypes = OutputArgDict(conf.get_dtype, default=None)
        self.output_formats = OutputArgDict(str, default=self.config.default_file_format)
        self.output_csv_separators = OutputArgDict(str, default=conf.FILE_FORMAT_CSV_SEPARATOR)
        self.output_text_delimiters = OutputArgDict(str, default=conf.FILE_FORMAT_TEXT_DELIMITER)
        self.output_text_newlines = OutputArgDict(str, default=conf.FILE_FORMAT_TEXT_NEWLINE)
        self.output_text_converters = OutputArgDict(str, default=conf.FILE_FORMAT_TEXT_CONVERTER)

        self.expressions = ArgList(str)

        default_dtype = conf.get_dtype(self.config.default_data_type)
        self.logger = log.LOGGER

        self.set_accept_bigger_raw_files(False)
        self.set_read_mode(conf.DEFAULT_READ_MODE)
        self.set_optimized_min_size(self.config.default_optimized_min_size)
        self.set_memory_limit(self.config.default_memory_limit)
        self.set_split_dimensions(None)
        self.set_clobber(self.config.default_clobber)
        self.set_visualizer_options()
        self.set_print_report(False)
        self.set_histogram_options(False)
        self.set_dry_run(False)
        self.set_dtype(default_dtype)

        self.total_read_bytes = 0
        self.input_cubes = OrderedDict()

        self._used_input_filenames = set()
        self._used_output_filenames = set()

        self._result = None
        self._locals = {}
        self._pointless_expressions = []
        cubes_internals.set_output_mode_callback(self.notify_output_mode)

        self._controller = None
        self._stats_infos = []
        self._diff_cubes = []

    def log(self, level, message):
        if level > logging.INFO:
            format = "{header}{level}: {message}"
        else:
            format = "{header}{message}"
        self.logger.log(level, format.format(header=self._log_header, level=logging.getLevelName(level), message=message))

    def log_debug(self, message):
        self.log(logging.DEBUG, message)

    def log_info(self, message):
        self.log(logging.INFO, message)

    def log_warning(self, message):
        self.log(logging.WARNING, message)

    def log_error(self, message):
        self.log(logging.ERROR, message)

    def log_critical(self, message):
        self.log(logging.CRITICAL, message)

    def show_logo(self):
        log.PRINT(RUBIK)

    def show_logo_once(self):
        attr_name = '_logo_has_been_shown'
        if not getattr(self, attr_name, False):
            self.show_logo()
            setattr(self, attr_name, True)

    def set_dry_run(self, dry_run):
        self.dry_run = dry_run

    def set_dtype(self, dtype):
        self.dtype = dtype
        cubes_internals.set_default_dtype(self.dtype)
        self.dtype_bytes = self.dtype().itemsize
        self._cache_dtype_bytes = {self.dtype: self.dtype_bytes}

    def set_logger(self, logger, report_logger=None):
        if report_logger is None:
            report_logger = logger
        self.logger = logger
        self.report_logger = report_logger

    def set_accept_bigger_raw_files(self, accept_bigger_raw_files):
        self.accept_bigger_raw_files = accept_bigger_raw_files

    def set_read_mode(self, read_mode):
        self.read_mode = read_mode

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

    def set_visualizer_options(self,
            controller_type=None,
            visualizer_type=None,
            visualizer_attributes=None,
            visualizer_attribute_files=None):
        self.controller_type = controller_type
        self.visualizer_type = visualizer_type
        self.visualizer_attributes = visualizer_attributes
        self.visualizer_attribute_files = visualizer_attribute_files

    def set_histogram_options(self, bins=10, length=80, range=None, mode=None, decimals=None):
        self.histogram_bins = bins
        self.histogram_range = range
        self.histogram_length = length
        fmt_base = "{b}{s_start:{l_start}s}, {s_end:{l_end}s}{k}|{h}|"
        fmt_num = fmt_base + "{s_num:>{l_num}s}"
        fmt_percentage = fmt_base + "{s_percentage:>{l_percentage}s}"
        if mode is None:
            mode = 'num'
        self.histogram_mode = mode
        if self.histogram_mode == "num":
            self.histogram_fmt = fmt_num
        elif self.histogram_mode == "percentage":
            self.histogram_fmt = fmt_percentage
        else:
            raise ValueError("invalid histogram mode {!r}".format(mode))
        self.histogram_decimals = decimals

    def set_print_report(self, print_report):
        self.print_report = print_report

    def run(self):
        if self.print_report:
            self._print_report()
        if not self.dry_run:
            self.initialize()
            self.evaluate_expressions(*self.expressions)
            self.finalize()
    
    def get_dtype_bytes(self, dtype):
        if not dtype in self._cache_dtype_bytes:
            self._cache_dtype_bytes[dtype] = dtype().itemsize
        return self._cache_dtype_bytes[dtype]

    def register_input_cube(self, input_label, input_filename, cube):
        self.input_cubes[input_label] = cube

    def result(self):
        return self._result

    def set_labeled_attributes(self, label, attributes):
        for attribute_name, attribute_value in attributes.items():
            if attribute_value is not None:
                if label is None: 
                    option = str(attribute_value)
                else:
                    option = "{}={}".format(label, attribute_value)
                attribute_label, attribute_value = getattr(self, attribute_name + 's').add(option)
                attributes[attribute_name] = attribute_value

    def get_label_filename(self, function_name, adict, label, filename, attributes):
        if label is None:
            if filename is None:
                raise RubikError("invalid call to {}: missing both label and filename arguments".format(function_name))
            else:
                result = adict.add(filename)
                self.set_labeled_attributes(label, attributes)
                return result
        else:
            if filename is not None:
                result = adict.add("{}={}".format(label, filename))
                self.set_labeled_attributes(label, attributes)
                return result
            else:
                result = label, adict[label]
                return result
       

    def read_cube(self,
        filename=None,
        label=None,
        shape=None,
        extractor=None,
        mode=None,
        offset=None,
        dtype=None,
        format=None,
        csv_separator=None,
        text_delimiter=None,
    ):
        attributes = dict(
            shape=shape, 
            extractor=extractor, 
            input_mode=mode, 
            input_offset=offset, 
            input_dtype=dtype, 
            input_format=format, 
            input_csv_separator=csv_separator, 
            input_text_delimiter=text_delimiter, 
        )
        input_label, input_filename = self.get_label_filename('read_cube', self.input_filenames, label, filename, attributes)
        return self.read_cube_impl(input_label, input_filename, attributes=attributes)

    def initialize(self):
        pass

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
        self.log_debug("trying to read {0} bytes and extract {1} bytes; already read {2} bytes...".format(
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

    def read_cube_impl(self, input_label, input_filename, attributes):
        self._check_memory_limit(input_label, input_filename)
        if self.read_mode == conf.READ_MODE_SAFE:
            return self.read_cube_impl_safe(input_label, input_filename, attributes)
        elif self.read_mode == conf.READ_MODE_OPTIMIZED:
            return self.read_cube_impl_optimized(input_label, input_filename, attributes)
        else:
            raise RubikError("invalid read mode {0!r}".format(self.read_mode))

    def get_attribute(self, attribute_name, attributes, label, ordinal):
        attribute_value = attributes.get(attribute_name, None)
        if attribute_value is not None:
            return attribute_value
        else:
            attribute_value = getattr(self, attribute_name + 's').get(label, ordinal)
            return attribute_value
        
    def read_cube_impl_safe(self, input_label, input_filename, attributes):
        self.log_debug("executing safe read...")
        input_ordinal = self.input_filenames.get_ordinal(input_label)
        shape = self.get_attribute('shape', attributes, input_label, input_ordinal)
        if shape is None:
            raise RubikError("missing shape for filename {0}".format(input_filename))
        input_format = self.get_attribute('input_format', attributes, input_label, input_ordinal)
        if input_format is None:
            input_format = conf.DEFAULT_FILE_FORMAT
        input_mode = self.get_attribute('input_mode', attributes, input_label, input_ordinal)
        if input_mode is None:
            input_mode = 'rb'
        else:
            input_mode = input_mode.mode
        input_offset = self.get_attribute('input_offset', attributes, input_label, input_ordinal)
        input_dtype = self.get_attribute('input_dtype', attributes, input_label, input_ordinal)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        extractor = self.get_attribute('extractor', attributes, input_label, input_ordinal)
        assert isinstance(input_filename, InputFilename), "not an InputFilename: {!r} [{}]".format(input_filename, type(input_filename))
        assert (extractor is None) or isinstance(extractor, Extractor), "not a valid extractor: {!r} [{}]".format(extractor, type(extractor))
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
            input_csv_separator = self.get_attribute('input_csv_separator', attributes, input_label, input_ordinal)
            numpy_function_nargs['sep'] = input_csv_separator
        elif input_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            # read all elements (must check number of elements)
            numpy_function = np.loadtxt
            input_text_delimiter = self.get_attribute('input_text_delimiter', attributes, input_label, input_ordinal)
            if input_text_delimiter is not None:
                numpy_function_nargs['delimiter'] = input_text_delimiter
        else:
            raise RubikError("invalid file format {0!r}".format(input_format))
        input_filename = format_filename(input_filename, shape.shape(), input_format, input_dtype)
        input_filename = self._check_input_filename(shape, input_format, input_filename, input_dtype, input_offset)
        self.log_info("reading {c} {t!r} elements {b}from {f!r} file {i!r}...".format(
            c=expected_input_count,
            t=input_dtype.__name__,
            b=msg_bytes,
            f=input_format,
            i=input_filename))
        with open(input_filename, input_mode) as f_in:
            if input_offset is not None:
                offset = input_offset.get_bytes()
                self.log_info("seeking {f!r}@{o}...".format(
                    f=input_filename,
                    o=offset,
                ))
                f_in.seek(offset)
            array = numpy_function(f_in, dtype=input_dtype, *numpy_function_pargs, **numpy_function_nargs)
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

    def read_cube_impl_optimized(self, input_label, input_filename, attributes):
        self.log_debug("executing optimized read...")
        input_ordinal = self.input_filenames.get_ordinal(input_label)
        shape = self.get_attribute('shape', attributes, input_label, input_ordinal)
        if shape is None:
            raise RubikError("missing shape for filename {0}".format(input_filename))
        input_format = self.get_attribute('input_format', attributes, input_label, input_ordinal)
        if input_format is None:
            input_format = conf.DEFAULT_FILE_FORMAT
        input_mode = self.get_attribute('input_mode', attributes, input_label, input_ordinal)
        if input_mode is None:
            input_mode = 'rb'
        else:
            input_mode = input_mode.mode
        input_offset = self.get_attribute('input_offset', attributes, input_label, input_ordinal)
        input_dtype = self.get_attribute('input_dtype', attributes, input_label, input_ordinal)
        if input_dtype is None:
            input_dtype = self.dtype
        input_dtype_bytes = self.get_dtype_bytes(input_dtype)
        extractor = self.get_attribute('extractor', attributes, input_label, input_ordinal)
        assert isinstance(input_filename, InputFilename), "not an InputFilename: {!r} [{}]".format(input_filename, type(input_filename))
        assert (extractor is None) or isinstance(extractor, Extractor), "not a valid extractor: {!r} [{}]".format(extractor, type(extractor))
        input_filename = input_filename.filename
        if not isinstance(shape, Shape):
            shape = Shape(shape)
        if extractor:
            expected_input_count, expected_read_count = extractor.get_counts(shape)
        else:
            expected_input_count = shape.count()
            expected_read_count = expected_input_count
        numpy_function = cubes_api.fromfile_generic
        numpy_function_nargs = {}
        numpy_function_pargs = []
        if input_format == conf.FILE_FORMAT_RAW:
            num_bytes = expected_read_count * input_dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
        elif input_format == conf.FILE_FORMAT_CSV:
            msg_bytes = ''
            input_csv_separator = self.get_attribute('input_csv_separator', attributes, input_label, input_ordinal)
            numpy_function_nargs['sep'] = input_csv_separator
        elif input_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            input_text_delimiter = self.get_attribute('input_text_delimiter', attributes, input_label, input_ordinal)
            if input_text_delimiter is not None:
                numpy_function_nargs['delimiter'] = input_text_delimiter
        else:
            raise RubikError("invalid file format {0!r}".format(input_format))
        input_filename = format_filename(input_filename, shape.shape(), input_format, input_dtype)
        input_filename = self._check_input_filename(shape, input_format, input_filename, input_dtype, input_offset)
        if extractor is None:
            extractor_msg = ''
        else:
            extractor_msg = "[{0}]".format(extractor)
        self.log_info("reading {c} {t!r} elements {b}from {f!r} file {i!r}{x}...".format(
            c=expected_read_count,
            t=input_dtype.__name__,
            b=msg_bytes,
            f=input_format,
            i=input_filename,
            x=extractor_msg))
        with open(input_filename, input_mode) as f_in:
            if input_offset is not None:
                offset = input_offset.get_bytes()
                self.log_info("seeking {f!r}@{o}...".format(
                    f=input_filename,
                    o=offset,
                ))
                f_in.seek(offset)
            cube = numpy_function(input_format, f_in, shape=shape, extractor=extractor, dtype=input_dtype, min_size=self.optimized_min_size, *numpy_function_pargs, **numpy_function_nargs)
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

    def iterate_on_split(self, function, cube, *p_args, **n_args):
        if cube is None:
            cube = self._result
        for cube, dlabels in self.split_over_dimensions(cube):
            function(cube=cube, dlabels=dlabels, *p_args, **n_args)
        
    def finalize(self):
        for expression in self._pointless_expressions:
            self.log_warning("pointless expression {!r}".format(expression))
        cube = self._result
        self.run_controller()
        self.print_stats_infos()
        self.print_diff()
    
    def notify_output_mode(self):
        del self._pointless_expressions[:]

    def write_cube(self, filename=None, label=None, cube=None,
        mode=None,
        offset=None,
        dtype=None,
        format=None,
        csv_separator=None,
        text_delimiter=None,
        text_newline=None,
        text_converter=None,
    ):
        attributes = dict(
            output_mode=mode,
            output_offset=offset,
            output_dtype=dtype,
            output_format=format,
            output_csv_separator=csv_separator,
            output_text_delimiter=text_delimiter,
            output_text_newline=text_newline,
            output_text_converter=text_converter,
        )
        self.notify_output_mode()
        output_label, output_filename = self.get_label_filename('write_cube', self.output_filenames, label, filename, attributes)
        if cube is None:
            cube = self._result
        self.iterate_on_split(self.write_cube_impl, cube, output_label=output_label, output_filename=output_filename, attributes=attributes)

    def write_cube_impl(self, output_filename, output_label, cube, dlabels, attributes):
        output_ordinal = self.output_filenames.get_ordinal(output_label)
        output_format = self.get_attribute('output_format', attributes, output_label, output_ordinal)
        if output_format is None:
            output_format = conf.DEFAULT_FILE_FORMAT
        output_dtype = self.get_attribute('output_dtype', attributes, output_label, output_ordinal)
        if output_dtype is None:
            output_dtype = self.dtype
        output_dtype_bytes = self.get_dtype_bytes(output_dtype)
        if cube.dtype != output_dtype:
            cube = cube.astype(output_dtype)
        assert isinstance(output_filename, OutputFilename), "not an OutputFilename: {!r} [{}]".format(output_filename, type(output_filename))
        output_filename = output_filename.filename
        numpy_function = None
        numpy_function_pargs = []
        numpy_function_nargs = {}
        output_filename = format_filename(output_filename, cube.shape, output_format, output_dtype, keywords=dlabels)
        output_offset = self.get_attribute('output_offset', attributes, output_label, output_ordinal)
        output_mode = self.get_attribute('output_mode', attributes, output_label, output_ordinal)
        if output_mode is None:
            if output_offset is not None:
                if os.path.lexists(output_filename):
                    output_mode = OutputMode("r+b")
                else:
                    output_mode = OutputMode("w+b")
            else:
                output_mode = OutputMode("wb")
        self._check_output_filename(output_filename)
        if output_format == conf.FILE_FORMAT_RAW:
            num_bytes = cube.size * output_dtype_bytes
            msg_bytes = "({b} bytes) ".format(b=num_bytes)
            numpy_function = cube.tofile
            #numpy_function_pargs.append(output_filename)
        elif output_format == conf.FILE_FORMAT_CSV:
            msg_bytes = ''
            numpy_function = cube.tofile
            output_csv_separator = self.get_attribute('output_csv_separator', attributes, output_label, output_ordinal)
            numpy_function_nargs['sep'] = output_csv_separator
            #numpy_function_pargs.append(output_filename)
        elif output_format == conf.FILE_FORMAT_TEXT:
            msg_bytes = ''
            numpy_function = np.savetxt
            #numpy_function_pargs.append(output_filename)
            if len(cube.shape) <= 2:
                c2d = cube
            else:
                c2d = cube.reshape((cube.shape[0], cube.size // cube.shape[0]))
            numpy_function_pargs.append(c2d)
            output_text_delimiter = self.get_attribute('output_text_delimiter', attributes, output_label, output_ordinal)
            output_text_newline = self.get_attribute('output_text_newline', attributes, output_label, output_ordinal)
            output_text_converter = self.get_attribute('output_text_converter', attributes, output_label, output_ordinal)
            if output_text_delimiter is not None:
                numpy_function_nargs['delimiter'] = output_text_delimiter
            if output_text_newline is not None:
                numpy_function_nargs['newline'] = output_text_newline
            if output_text_converter is not None:
                numpy_function_nargs['fmt'] = output_text_convert
        else:
            raise RubikError("invalid file format {0!r}".format(output_format))
        if output_mode.is_append_mode():
            omode = 'appending'
        else:
            omode = 'writing'
        self.log_info("{m} {c} {t!r} elements {b}to {f!r} file {o!r}...".format(
            m=omode,
            c=cube.size,
            t=output_dtype.__name__,
            b=msg_bytes,
            f=output_format,
            o=output_filename))
        with open(output_filename, output_mode.mode) as f_out:
            if output_offset is not None:
                offset = output_offset.get_bytes()
                self.log_info("seeking {f!r}@{o}...".format(
                    f=output_filename,
                    o=offset,
                ))
                f_out.seek(offset)
            numpy_function(f_out, *numpy_function_pargs, **numpy_function_nargs)

    def _log_dlabels(self, dlabels):
        if dlabels:
            dlabels_message = "## " + ', '.join("{0}={1}".format(dlabel, dvalue) for dlabel, dvalue in dlabels.items())
            log.PRINT(dlabels_message)

    def print_cube(self, cube=None):
        self.notify_output_mode()
        self.iterate_on_split(self.print_cube_impl, cube)

    def print_cube_impl(self, cube, dlabels):
        log.PRINT(cube)

    def print_stats(self, cube=None):
        self.notify_output_mode()
        self.iterate_on_split(self.print_stats_impl, cube)

    def print_stats_impl(self, cube, dlabels):
        if not isinstance(cube, np.ndarray):
            raise RubikError("cannot stat result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
        cubes_api.print_stats(cube, print_function=log.PRINT)

    def compare_stats(self, cube=None, title=""):
        if cube is None:
            cube = self._result
        self.notify_output_mode()
        self._stats_infos.append(cubes_api.stats_info(cube, name=title))
        
    def diff(self, cube=None, title=""):
        if cube is None:
            cube = self._result
        self.notify_output_mode()
        # keeps the last two cubes
        self._diff_cubes.append(cube)
        if len(self._diff_cubes) > 2:
            raise RubikError("cannot diff more than 2 cubes")
        
    def print_histogram(self, cube=None, bins=None, hrange=None, decimals=None, fmt=None):
        self.notify_output_mode()
        self.iterate_on_split(self.print_histogram_impl, cube, bins=bins, hrange=hrange, decimals=decimals, fmt=fmt)

    def print_histogram_impl(self, cube, dlabels, bins=None, hrange=None, decimals=None, fmt=None):
        if cube is None:
            cube = self._result
        if bins is None:
            bins = self.histogram_bins
        if hrange is None:
            hrange = self.histogram_range
        if decimals is None:
            decimals = self.histogram_decimals
        if fmt is None:
            fmt = self.histogram_fmt
        if not isinstance(cube, np.ndarray):
            raise RubikError("cannot make an histogram from result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
        histogram, bins = np.histogram(cube, bins=bins, range=hrange)
        start = bins[0]
        d_min = None
        for end in bins[1:]:
            d = abs(end - start)
            if d_min is None or d < d_min:
                d_min = d
        if decimals is None:
            power = 0
            f_d_min = d_min - int(d_min)
            if f_d_min > 0:
                while True:
                    if int(f_d_min * 10 ** power) > 0:
                        break
                    power += 1
            else:
                power = 0
        else:
            power = decimals
        if power:
            fmt_float = "{{:.{power}f}}".format(power=power)
        else:
            fmt_float = "{{:f}}".format()
        start = bins[0]
        l = []
        num_max = 0
        l_num, l_percentage, l_start, l_end = 0, 0, 0, 0
        num_tot = histogram.sum()
        for num, end in zip(histogram, bins[1:]):
            s_num = str(num)
            fraction = float(num) / num_tot
            s_percentage = "{:.2%}".format(fraction)
            s_start = fmt_float.format(start)
            s_end = fmt_float.format(end)
            if len(s_num) > l_num:
                l_num = len(s_num)
            if len(s_percentage) > l_percentage:
                l_percentage = len(s_percentage)
            if len(s_start) > l_start:
                l_start = len(s_start)
            if len(s_end) > l_end:
                l_end = len(s_end)
            l.append((num, s_num, s_percentage, s_start, s_end))
            if num > num_max:
                num_max = num
            start = end
        
        fixed_text = fmt.format(
            b='[',
            s_start='',
            l_start=l_start,
            s_end='',
            l_end=l_end,
            k=']',
            h='',
            s_num='',
            l_num=l_num,
            s_percentage='',
            l_percentage=l_percentage)
        text_length = len(fixed_text)
        h_max = max(0, self.histogram_length - text_length)
        b = '['
        for c, (num, s_num, s_percentage, s_start, s_end) in enumerate(l):
            if c == len(l) - 1:
                k = ']'
            else:
                k = ')'
            l_l = int(0.5 + (h_max * num) / float(num_max))
            l_r = h_max - l_l
            #log.PRINT("@@@ h_max={}, num={}, num_max={}, l_l={}, l_r={}".format(h_max, num, num_max, l_l, l_r))
            h = '*' * l_l + ' ' * l_r
            log.PRINT(fmt.format(
                s_num=s_num,
                l_num=l_num,
                s_percentage=s_percentage,
                l_percentage=l_percentage,
                s_start=s_start,
                l_start=l_start,
                s_end=s_end,
                l_end=l_end,
                h=h,
                b=b,
                k=k,
            ))

    def _check_output_filename(self, output_filename):
        if (not self.clobber) and os.path.exists(output_filename):
            raise RubikError("output file {0!r} already exists".format(output_filename))
        if output_filename in self._used_output_filenames:
            self.log_warning("output filename {0!r} already written".format(output_filename))
        self._used_output_filenames.add(output_filename)

    def _check_input_filename(self, shape, input_format, input_filename, input_dtype, input_offset):
        if input_filename in self._used_input_filenames:
            self.log_warning("input filename {0!r} already read".format(input_filename))
        self._used_input_filenames.add(input_filename)
        if input_offset is not None:
            accept_bigger_raw_files = True
            offset = input_offset.get_bytes()
        else:
            accept_bigger_raw_files = self.accept_bigger_raw_files
            offset = 0

        if not isinstance(shape, Shape):
            shape = Shape(shape)
        if not os.path.isfile(input_filename):
            raise RubikError("missing input file {0}".format(input_filename))
        if input_format == conf.FILE_FORMAT_RAW:
            expected_input_count = shape.count()
            expected_input_bytes = expected_input_count * self.get_dtype_bytes(input_dtype)
            input_stat_result = os.stat(input_filename)
            input_bytes = input_stat_result.st_size - offset
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
                if accept_bigger_raw_files:
                    warnings.warn(RuntimeWarning(message))
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
        self.log_info("extracting '{0}'...".format(extractor))
        subcube = cube[extractor.index_pickers()]
        return subcube
 
    def evaluate_expressions(self, *expressions):
        globals_d = {
            'np': np,
            'numpy': np,
            'cb': cubes_api,
            'cubes': cubes_api,
            'read_cube': self.read_cube,
            'write_cube': self.write_cube,
            'print_stats': self.print_stats,
            'print_cube': self.print_cube,
            'print_histogram': self.print_histogram,
            'compare_stats': self.compare_stats,
            'diff': self.diff,
            'view': self.view,
        }
        locals_d = {
            '_r': self._result,
        }
        result = self._result
        for expression in expressions:
            self._pointless_expressions.append(expression)
            globals_d.update(self.input_cubes)
            globals_d['_i'] = list(self.input_cubes.values())
            if expression.startswith('@'):
                source_filename = expression[1:]
                self.log_info("loading source from file {0!r}...".format(source_filename))
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
                self.log_info("evaluating expression {0!r}...".format(expression))
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
                self.log_debug("executing {0!r} expression...".format(mode))
                result = eval(compiled_expression, globals_d, locals_d)
                if mode == 'eval':
                    if result is not None:
                        self._result = result
                        locals_d['_r'] = self._result
                else:
                    result = locals_d.get('_r', None)
                    if result is not None:
                        self._result = result
                #print "expression: {!r} -> {!r}".format(expression, locals_d['_r'])
            except Exception as err:
                raise RubikError("cannot evaluate expression {0!r}: {1}: {2}".format(expression, type(err).__name__, err))
            #if result.dtype != self.dtype:
            #    result = result.astype(self.dtype)
        
    def _print_report(self):
        def _log(condition):
            if condition:
                return self.report_logger.info
            else:
                return self.report_logger.debug
        logger = self.report_logger
        logger.info("### Settings")
        logger.info("Internal dtype: {}".format(self.dtype.__name__))
        logger.info("  bytes: {}".format(self.dtype_bytes))
        logger.info("")
        if self.input_filenames:
            logger.info("### Input files")
            for input_label, input_filename in self.input_filenames.items():
                input_mode = self.input_modes.get(input_filename, input_label)
                input_offset = self.input_offsets.get(input_filename, input_label)
                input_dtype = self.input_dtypes.get(input_filename, input_label)
                if input_dtype is not None:
                    input_dtype = input_dtype.__name__
                input_format = self.input_formats.get(input_filename, input_label)
                input_csv_separator = self.input_csv_separators.get(input_filename, input_label)
                input_text_delimiter = self.input_text_delimiters.get(input_filename, input_label)
                input_shape = self.shapes.get(input_filename, input_label)
                input_extractor = self.extractors.get(input_filename, input_label)
                logger.info("Input file {!r} [{}]".format(input_filename, input_label))
                logger.info("  shape = {!s} [{}]".format(input_shape, input_shape.count()))
                _log(input_extractor)("  extractor = {!r}".format(str(input_extractor)))
                _log(input_mode)("  mode = {!s}".format(input_mode))
                _log(input_offset)("  offset = {!s}".format(input_offset))
                _log(input_dtype)("  dtype = {!s}".format(input_dtype))
                _log(input_format)("  format = {!s}".format(input_format))
                _log(input_format == conf.FILE_FORMAT_CSV) ("    csv separator = {!r}".format(input_csv_separator))
                _log(input_format == conf.FILE_FORMAT_TEXT)("    text delimiter = {!r}".format(input_text_delimiter))
            logger.info("")
    
        if self.output_filenames:
            logger.info("### Output files")
            for output_label, output_filename in self.output_filenames.items():
                output_mode = self.output_modes.get(output_filename, output_label)
                output_offset = self.output_offsets.get(output_filename, output_label)
                output_dtype = self.output_dtypes.get(output_filename, output_label)
                if output_dtype is not None:
                    output_dtype = output_dtype.__name__
                output_format = self.output_formats.get(output_filename, output_label)
                output_csv_separator = self.output_csv_separators.get(output_filename, output_label)
                output_text_delimiter = self.output_text_delimiters.get(output_filename, output_label)
                output_text_newline = self.output_text_newlines.get(output_filename, output_label)
                output_text_converter = self.output_text_converters.get(output_filename, output_label)
                logger.info("Output file {!r} [{}]".format(output_filename, output_label))
                _log(output_mode)("  mode = {!s}".format(output_mode))
                _log(output_offset)("  offset = {!s}".format(output_offset))
                _log(output_dtype)("  dtype = {!s}".format(output_dtype))
                _log(output_format)("  format = {!s}".format(output_format))
                _log(output_format == conf.FILE_FORMAT_CSV) ("    csv separator = {!r}".format(output_csv_separator))
                _log(output_format == conf.FILE_FORMAT_TEXT)("    text delimiter = {!r}".format(output_text_delimiter))
                _log(output_format == conf.FILE_FORMAT_TEXT)("    text newline = {!r}".format(output_text_newline))
                _log(output_format == conf.FILE_FORMAT_TEXT)("    text converter = {!r}".format(output_text_converter))
            logger.info("")

        if self.expressions:
            logger.info("### Expressions")
            for expression_num, expression in enumerate(self.expressions):
                logger.info("Expression[{}]: {!r}".format(expression_num, expression))
            logger.info("")
    
        logger.info("### Commands")
        logger.info("Histogram options:")
        logger.info("  bins = {}".format(self.histogram_bins))
        logger.info("  range = {}".format(self.histogram_range))
        logger.info("  length = {}".format(self.histogram_length))
        logger.info("  mode = {}".format(self.histogram_mode))
        logger.info("  decimals = {}".format(self.histogram_decimals))
        logger.info("Visualizer options:")
        logger.info("  controller_type = {}".format(self.controller_type))
        logger.info("  visualizer_type = {}".format(self.visualizer_type))
        logger.info("  visualizer_attributes = {}".format(self.visualizer_attributes))
        logger.info("  visualizer_attribute_files = {}".format(self.visualizer_attribute_files))

    def do_viewer(self, cube=None):
        if cube is None:
            cube = self._result
      
    def get_controller(self, cube=None):
        if cube is None:
            cube = self._result
        if self._controller is None:
            self._controller = controller_builder(
                logger=self.logger,
                controller_type=self.controller_type,
                data=cube,
                attributes=self.visualizer_attributes,
                attribute_files=self.visualizer_attribute_files,
                title="Controller",
            )
        return self._controller

    controller = property(get_controller)

    def view(self, cube=None, visualizer_type=None, title=None):
        self.notify_output_mode()
        if cube is None:
            cube = self._result
        if visualizer_type is None:
            visualizer_type = self.visualizer_type
        visualizer = visualizer_builder(
            logger=self.logger,
            title=title,
            visualizer_type=visualizer_type,
            controller=self.controller,
            data=cube,
        )
      
    def run_controller(self):
        if self._controller is not None:
            self.controller.run()

    def print_stats_infos(self):
        if self._stats_infos:
            log.PRINT(cubes_api.StatsInfo.reports(instances=self._stats_infos))

    def print_diff(self):
        if self._diff_cubes:
            if len(self._diff_cubes) == 1:
                raise RubikError("cannot compare 1 cube")
            else:
                info = cubes_api.diff_info(*self._diff_cubes)
                log.PRINT(info.report())
