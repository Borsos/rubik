#!/usr/bin/env python
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

__all__ = [
           'main',
          ]
import sys
import argparse

import random
import itertools

import numpy as np

from .. import conf
from ..units import Memory
from ..errors import RubikError, RubikMemoryError, RubikExpressionError

from ..application import log
from ..application import logo
from ..application import utils
from ..application import help_functions
from ..application.rubik import Rubik
from ..application.config import get_config
from ..application.argument_parser import CommandLineArgumentParser
from ..cubes.api import set_random_seed

_EXPRNUM = 0
def expression_type(value):
    global _EXPRNUM
    t = _EXPRNUM
    _EXPRNUM += 1
    return (t, value)

def key_value_type(value):
    if not '=' in value:
        raise ValueError("invalid <key=value> argument {!r}".format(value))
    k, v = value.split('=', 2)
    return k.strip(), v.strip()

class RubikAction(argparse.Action):
    RUBIK = None

class RubikPrintAction(RubikAction):
    pass

class RubikPrintVersionAction(RubikPrintAction):
    def __init__(self,
             option_strings,
             version,
             nargs=0,
             dest=argparse.SUPPRESS,
             default=argparse.SUPPRESS,
             ):
        super(RubikPrintVersionAction, self).__init__(
             option_strings=option_strings,
             dest=dest,
             nargs=nargs,
             default=default)
        self.version = version

    def __call__(self, parser, namespace, values, option_string):
        stream = log.get_stderr()
        stream.write(self.version + '\n')

class RubikPrintLogoAction(RubikPrintAction):
    def __init__(self,
             option_strings,
             help,
             nargs=0,
             dest=argparse.SUPPRESS,
             default=argparse.SUPPRESS,
             ):
        super(RubikPrintLogoAction, self).__init__(
             option_strings=option_strings,
             dest=dest,
             nargs=nargs,
             default=default)
        self.help = help

    def __call__(self, parser, namespace, values, option_string):
        stream = log.get_stderr()
        stream.write(logo.RUBIK + '\n')
        parser.exit()

class RubikPrintHelpAction(RubikPrintAction):
    def __call__(self, parser, namespace, values, option_string):
        parser.print_help(file=log.get_stderr())

class RubikPrintUsageAction(RubikPrintAction):
    def __call__(self, parser, namespace, values, option_string):
        parser.print_usage(file=log.get_stderr())

class ConstExpressionAction(RubikAction):
    CONST = None
    def __call__(self, parser, namespace, values, option_string):
        self.RUBIK.expressions.store(self.CONST)
        
class PrintStatsAction(ConstExpressionAction):
    CONST = 'print_stats()'

class CompareStatsInfoAction(ConstExpressionAction):
    CONST = 'compare_stats()'

class DiffAction(ConstExpressionAction):
    CONST = 'diff()'

class PrintCubeAction(ConstExpressionAction):
    CONST = 'print_cube()'

class PrintHistogramAction(ConstExpressionAction):
    CONST = 'print_histogram()'

class VisualizeAction(ConstExpressionAction):
    CONST = 'view()'

class InputAction(RubikAction):
    def __call__(self, parser, namespace, values, option_string):
        for value in values:
            label, input_filename = self.RUBIK.input_filenames.add(value)
            self.RUBIK.expressions.store("read_cube(label={!r})".format(label))

class OutputAction(RubikAction):
    def __call__(self, parser, namespace, values, option_string):
        for value in values:
            label, output_filename = self.RUBIK.output_filenames.add(value)
            self.RUBIK.expressions.store("write_cube(label={!r})".format(label))

def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]

    try:
        config = get_config()
    except Exception as err:
        log.trace_error(False)

    description = """\
================================================================================
Rubik {version}
================================================================================
{logo}
Rubik is a command line tool to generate/read/transform/write N-dimensional
cubes. It is based on the numpy library.

Rubik can:
* create cubes from scratch;
* read input files containing N-dimensional cubes ('raw', 'text' or 'csv'
  formats are supported);
* extract a portion of the cube during read;
* execute generic expressions involving input cubes and producing other cubes;
* changing values on the cubes;
* writing cubes to output files ('raw', 'text' or 'csv' formats are supported).

""".format(version=conf.VERSION, logo=logo.RUBIK)
    epilog = ""
    
    rubik = Rubik()
    RubikAction.RUBIK = rubik

    parser = CommandLineArgumentParser(
        #fromfile_prefix_chars='%',
        description=description,
        epilog=epilog,
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    global_group = parser.add_argument_group(
        "global options",
        description="""\
Global options""")

    global_group.add_argument("--verbose", "-v",
        dest="verbose_level",
        action="count",
        default=config.default_verbose_level,
        help="increase verbose level")

    global_group.add_argument("--verbose-level",
        metavar="VL",
        dest="verbose_level",
        type=int,
        default=config.default_verbose_level,
        help="set verbose level")

    global_group.add_argument("--quiet", "--silent", "-q",
        dest="verbose_level",
        action="store_const",
        const=0,
        default=config.default_verbose_level,
        help="set quiet mode (warning messages are disabled)")

    global_group.add_argument("--report", "-R",
        dest="report_level",
        action="count",
        default=config.default_report_level,
        help="increase report level")

    global_group.add_argument("--dry-run", "-d",
        dest="dry_run",
        action="store_true",
        default=False,
        help="dry run")

    global_group.add_argument("--version",
        action=RubikPrintVersionAction,
        version='{program} {version}'.format(program=conf.PROGRAM_NAME, version=conf.VERSION))

    global_group.add_argument("--logo", "-L",
        action=RubikPrintLogoAction,
        help="show rubik's logo")

    global_group.add_argument("--trace-errors", "-E",
        dest="trace_errors",
        action="store_true",
        default=config.default_trace_errors,
        help="show error traceback")

    global_group.add_argument("--safe",
        dest="read_mode",
        action="store_const",
        const=conf.READ_MODE_SAFE,
        default=config.default_read_mode,
        help="safe read mode")

    global_group.add_argument("--optimized",
        dest="read_mode",
        action="store_const",
        const=conf.READ_MODE_OPTIMIZED,
        default=config.default_read_mode,
        help="safe read mode")

    global_group.add_argument("--optimized-min-size",
        metavar="S",
        dest="optimized_min_size",
        type=Memory,
        default=config.default_optimized_min_size,
        help="switch from optimized to safe read mode when reading less than C bytes (a huge value is equivalent to --safe)")

    global_group.add_argument("--memory-limit", "-m",
        metavar="L[units]",
        dest="memory_limit",
        type=Memory,
        default=config.default_memory_limit,
        help="when more than the given limit is needed for a single extracted cube, raise an error")

    global_group.add_argument("--dtype", "-t",
        metavar="D",
        dest="dtype",
        type=conf.get_dtype,
        default=config.default_data_type,
        help="data type name (--help-data-types/-hd to show all available data types)")

    global_group.add_argument("--accept-bigger-raw-files", "-a",
        action="store_true",
        default=False,
        help="if an input raw file is bigger than expected, simply issue a warning message")

    global_group.add_argument("--clobber",
        action="store_true",
        default=config.default_clobber,
        help="overwrite existing output files")

    global_group.add_argument("--no-clobber",
        action="store_false",
        default=config.default_clobber,
        help="do not overwrite existing output files")

    global_group.add_argument("--random-seed", "-r",
        type=int,
        default=None,
        help="set the random seed")

    global_group.add_argument("--warnings", "-W",
        action="append",
        choices=conf.ALL_WARNINGS,
        default=[],
        help="enable warnings")

    global_group.add_argument("--source-file", "-f",
        metavar="E",
        dest="source_files",
        type=lambda x: rubik.expressions.store('@' + x),
        nargs='+',
        help="add a source file (--help-expression/-he for more information)")

    global_group.add_argument("--expression", "-e",
        metavar="E",
        dest="expressions",
        type=rubik.expressions.store,
        nargs='+',
        help="add an expressions to evaluate (--help-expression/-he for more information)")

    global_group.add_argument("--test", "-T",
        dest="run_test",
        action="store_true",
        default=False,
        help="run test suites")

    global_group.add_argument("expression",
        type=rubik.expressions.store,
        nargs='*',
        help="add an expressions to evaluate (--help-expression/-he for more information)")

    input_group = parser.add_argument_group(
        "input options",
        description="""\
Options related to input files. All these options can be labeled;
see --help-labeled-options for more information.""")

    input_group.add_argument("--input-filename", "-i",
        metavar='I',
        dest="input_filenames",
        nargs='+',
        #type=rubik.input_filenames.store,
        action=InputAction,
        help="input filename (--help-filename/-hf for an explanation about filenames)")

    input_group.add_argument("--shape", "-s",
        metavar="[D0[:D1[...]]]",
        dest="shapes",
        type=rubik.shapes.store,
        help="shape of the input filename")

    input_group.add_argument("--extract", "-x",
        metavar="X",
        dest="extractors",
        type=rubik.extractors.store,
        help="subcube extractor (--help-extractor/-he for more information)")

    input_group.add_argument("--input-mode", "-Im",
        dest="input_modes",
        type=rubik.input_modes.store,
        help="input mode (e. g. \"r+b\")")

    input_group.add_argument("--input-offset", "-Io",
        dest="input_offsets",
        type=rubik.input_offsets.store,
        help="input offset")

    input_group.add_argument("--input-dtype", "-It",
        metavar="D",
        dest="input_dtypes",
        type=rubik.input_dtypes.store,
        help="input data type name (--help-data-types/-hd to show all available data types)")

    input_group.add_argument("--input-format", "-If",
        dest="input_formats",
        type=rubik.input_formats.store,
        help="input file format")

    input_group.add_argument("--input-csv-separator", "-Is",
        metavar='S',
        dest="input_csv_separators",
        type=rubik.input_csv_separators.store,
        help="separator to be used with '{0}' input file format".format(conf.FILE_FORMAT_CSV))

    input_group.add_argument("--input-text-delimiter", "-Id",
        metavar='D',
        dest="input_text_delimiters",
        type=rubik.input_text_delimiters.store,
        help="delimiter to be used with '{0}' input file format".format(conf.FILE_FORMAT_TEXT))

    output_group = parser.add_argument_group(
        "output options",
        description="""\
Options related to output files. All these options can be labeled;
see --help-labeled-options for more information.""")

    file_output_group = parser.add_argument_group(
        "file output arguments",
        description="""\
Arguments for output to files""")

    histogram_output_group = parser.add_argument_group(
        "histogram output arguments",
        description="""\
Arguments for histogram generation""")

    visualizer_group = parser.add_argument_group(
        "graphical visualizer arguments",
        description="""\
Arguments for graphical visualization""")

    write_output_filename_group = output_group.add_mutually_exclusive_group()
    write_output_filename_group.add_argument("--output-filename", "-o",
        metavar='O',
        dest="output_filenames",
        action=OutputAction,
        nargs='+',
        #type=rubik.output_filenames.store,
        help="output filename (--help-filename/-hf for an explanation about filenames)")

    output_group.add_argument('--print-cube', '--print', '-P',
        action=PrintCubeAction,
        nargs=0,
        help="print the result cube")

    global_group.add_argument("--print-stats", "--stats", "-S",
        action=PrintStatsAction,
        nargs=0,
        help="print statistics about the result cube")

    global_group.add_argument("--compare-stats", "-C",
        action=CompareStatsInfoAction,
        nargs=0,
        help="collect statistics about the result cube")

    global_group.add_argument("--diff", "-D",
        action=DiffAction,
        nargs=0,
        help="show differences")

    output_group.add_argument('--histogram', '-H',
        action=PrintHistogramAction,
        nargs=0,
        help="print an histogram; see histogram arguments below")

    output_group.add_argument('--view', '-V',
        action=VisualizeAction,
        nargs=0,
        help="view the result graphically; see graphical visualizer arguments below")

    histogram_output_group.add_argument('--histogram-bins', '-Hb',
        metavar="Hb",
        type=int,
        default=10,
        help="num of histogram bins")

    histogram_output_group.add_argument('--histogram-range', '-Hr',
        metavar="Hr",
        type=float,
        nargs=2,
        default=None,
        help="range of the histogram")

    histogram_output_group.add_argument('--histogram-decimals', '-Hd',
        metavar="Hd",
        type=int,
        default=None,
        help="number of decimals for bins")

    histogram_output_group.add_argument('--histogram-length', '-Hl',
        metavar="Hl",
        type=int,
        default=80,
        help="length of the histogram lines")

    histogram_output_group.add_argument('--histogram-percentage', '-Hp',
        metavar="Hp",
        dest="histogram_mode",
        action="store_const",
        const="percentage",
        default="num",
        help="show percentage of elements per bin")

    histogram_output_group.add_argument('--histogram-num', '-Hn',
        metavar="Hn",
        dest="histogram_mode",
        action="store_const",
        const="num",
        default="num",
        help="show number of elements per bin")

    visualizer_group.add_argument('--view-volume-slicer', '-Vs',
        dest="visualizer_type",
        action="store_const",
        const="VolumeSlicer",
        default="auto",
        help="view the 3d cube with VolumeSlicer class")

#    visualizer_group.add_argument('--view-volume-render', '-Vr',
#        dest="visualizer_type",
#        action="store_const",
#        const="VolumeRender",
#        default="auto",
#        help="view the 3d cube with VolumeRender class")
#
#    visualizer_group.add_argument('--view-volume-contour', '-Vc',
#        dest="visualizer_type",
#        action="store_const",
#        const="VolumeContour",
#        default="auto",
#        help="view the 3d cube with VolumeContour class")

    visualizer_group.add_argument('--view-auto', '-VA',
        dest="visualizer_type",
        action="store_const",
        const="auto",
        default="auto",
        help="view the result with default visualizer")

    visualizer_group.add_argument('--view-attribute', '-Va',
        metavar="VA",
        dest="visualizer_attributes",
        type=key_value_type,
        action="append",
        default=[],
        nargs='+',
        help="add a visualizer attribute (e.g. colormap=\"black-white\"; see --view-list/-Vl for a complete list of attributes)")

    visualizer_group.add_argument('--view-attribute-file', '-Vf',
        metavar="VF",
        dest="visualizer_attribute_files",
        type=str,
        action="append",
        default=[],
        help="load visualizer attributes from file")

    visualizer_group.add_argument('--view-list', '-Vl',
        dest="visualizer_list",
        action="store_true",
        default=False,
        help="show available graphical visualizers and attributes")

    output_group.add_argument("--split", "-l",
        metavar="D",
        dest="split_dimensions",
        type=int,
        action="append",
        default=[],
        help="split dimension D (--help-split/-hl for more information)")

    file_output_group.add_argument("--output-mode", "-Om",
        metavar="Om",
        dest="output_modes",
        type=rubik.output_modes.store,
        help="output mode (e. g. \"w+b\")")

    file_output_group.add_argument("--output-offset", "-Oo",
        metavar="Oo",
        dest="output_offsets",
        type=rubik.output_offsets.store,
        help="output offset")

    file_output_group.add_argument("--output-dtype", "-Ot",
        metavar="D",
        dest="output_dtypes",
        type=rubik.output_dtypes.store,
        help="output data type name (--help-data-types/-hd to show all available data types)")

    file_output_group.add_argument("--output-format", "-Of",
        metavar="Of",
        dest="output_formats",
        type=rubik.output_formats.store,
        help="output file format")

    file_output_group.add_argument("--output-csv-separator", "-Os",
        metavar='S',
        dest="output_csv_separators",
        type=rubik.output_csv_separators.store,
        help="separator to be used with '{0}' output file format".format(conf.FILE_FORMAT_CSV))

    file_output_group.add_argument("--output-text-delimiter", "-Od",
        metavar='D',
        dest="output_text_delimiters",
        type=rubik.output_text_delimiters.store,
        help="delimiter to be used with '{0}' output file format".format(conf.FILE_FORMAT_TEXT))

    file_output_group.add_argument("--output-text-newline", "-On",
        metavar='N',
        dest="output_text_newlines",
        type=rubik.output_text_newlines.store,
        help="newline to be used with '{0}' output file format".format(conf.FILE_FORMAT_TEXT))

    file_output_group.add_argument("--output-text-converter", "-Oc",
        metavar='C',
        dest="output_text_converters",
        type=rubik.output_text_converters.store,
        help="converter to be used with '{0}' output file format (e.g. '%%.18e')".format(conf.FILE_FORMAT_TEXT))

    test_group = parser.add_argument_group(
        "test options",
        description="""\
Options related to tests.""")

    test_group.add_argument("--test-pattern", "-Tp",
        metavar="SP[.TP]",
        dest="test_patterns",
        type=str,
        default=[],
        nargs='+',
        help="add pattern to filter suites/tests")

    test_group.add_argument("--test-list", "-Tl",
        dest="test_list",
        action="store_true",
        default=False,
        help="list available tests")

    test_group.add_argument("--test-verbose", "-Tv",
        dest="test_verbose_level",
        action="count",
        default=config.default_verbose_level,
        help="increase test verbose level")

    test_group.add_argument("--test-verbose-level", "-TV",
        dest="test_verbose_level",
        type=int,
        default=config.default_verbose_level,
        help="set test verbose level")

    help_group = parser.add_argument_group(
        "help options",
        description="""\
Options to show help on specific topics """)

    help_group.add_argument("--help", "-h",
        action=RubikPrintHelpAction,
        nargs=0,
        help="show this help message and exit")

    help_group.add_argument("--usage", "-u",
        action=RubikPrintUsageAction,
        nargs=0,
        help="show usage and exit")

    help_group.add_argument("--help-dtypes", "-ht",
        dest="help_dtypes",
        action="store_true",
        default=False,
        help="show available dtypes")

    help_group.add_argument("--help-labeled-options", "-ho",
        dest="help_labeled_options",
        action="store_true",
        default=False,
        help="show help about labeled options")

    help_group.add_argument("--help-expression", "-he",
        dest="help_expression",
        action="store_true",
        default=False,
        help="show help about generic expressions")

    help_group.add_argument("--help-extractor", "-hx",
        dest="help_extractor",
        action="store_true",
        default=False,
        help="show help about extractors")

    help_group.add_argument("--help-user-defined-variables", "-hV",
        dest="help_user_defined_variables",
        action="store_true",
        default=False,
        help="show help about user defined variables")

    help_group.add_argument("--help-numpy", "-hn",
        dest="help_numpy",
        action="store_true",
        default=False,
        help="show content of the numpy module")

    help_group.add_argument("--help-cubes", "-hc",
        dest="help_cubes",
        action="store_true",
        default=False,
        help="show content of the 'cubes' (or 'cb') module")

    help_group.add_argument("--help-filenames", "-hf",
        dest="help_filenames",
        action="store_true",
        default=False,
        help="show available keywords for filename interpolation")

    help_group.add_argument("--help-split", "-hl",
        dest="help_split",
        action="store_true",
        default=False,
        help="help about splitting dimensions")

    help_group.add_argument("--help-environment-variables", "-hE",
        dest="help_environment_variables",
        action="store_true",
        default=False,
        help="help about environment variables")

    help_group.add_argument("--help-creating-cubes", "-hC",
        dest="help_creating_cubes",
        action="store_true",
        default=False,
        help="how to create cubes from scratch")

    help_group.add_argument("--help-output", "-hO",
        dest="help_output",
        action="store_true",
        default=False,
        help="help about output")

    help_group.add_argument("--help-memory-usage", "-hM",
        dest="help_memory_usage",
        action="store_true",
        default=False,
        help="help about memory usage")

    help_group.add_argument("--help-usage", "-hu",
        dest="help_usage",
        action="store_true",
        default=False,
        help="help about usage: shows some examples and common recipes")

    help_group.add_argument("--demo",
        dest="help_demo",
        action="store_true",
        default=False,
        help="show demo")

    arguments = list(itertools.chain(config.default_options, conf.RUBIK_OPTIONS, arguments))

    try:
        args = parser.parse_args(arguments)
    except Exception as err:
        sys.stderr.write("error: {0}: {1}\n".format(err.__class__.__name__, err))
        return 1

    log.set_trace_errors(args.trace_errors)

    logger = log.set_logger(args.verbose_level)
    report_logger = log.set_report_logger(args.report_level)

    PRINT = log.get_print()

    conf.enable_warnings(*args.warnings)

    # test
    if args.test_list or args.run_test:
        test_logger = log.set_test_logger(args.test_verbose_level)
        patterns = utils.flatten_list(args.test_patterns, depth=1)
        from ..testing.rubik_test_main import RubikTestMain
        rubik_test_main = RubikTestMain(logger=test_logger, verbose_level=args.test_verbose_level)
        if args.test_list:
            for test_num, test_name in enumerate(rubik_test_main.filter_test_names(patterns)):
                PRINT("{:5d}) {}".format(test_num, test_name))
            #for test_name in rubik_test_main.filter_test_names(patterns):
            #    PRINT("  {}".format(test_name))
        if args.run_test:
            result = rubik_test_main.run(patterns)
            return_code = len(result.failures)
            return return_code
        return 0

    rubik.set_dry_run(args.dry_run)
    rubik.set_logger(logger, report_logger)
    rubik.set_accept_bigger_raw_files(args.accept_bigger_raw_files)
    rubik.set_read_mode(args.read_mode)
    rubik.set_optimized_min_size(args.optimized_min_size)
    rubik.set_memory_limit(args.memory_limit)
    rubik.set_split_dimensions(args.split_dimensions)
    rubik.set_clobber(args.clobber)
    rubik.set_visualizer_options(visualizer_type=args.visualizer_type, visualizer_attributes=utils.flatten_list(args.visualizer_attributes, depth=1), visualizer_attribute_files=args.visualizer_attribute_files)
    rubik.set_print_report(args.report_level > 0)
    rubik.set_histogram_options(
        bins=args.histogram_bins,
        range=args.histogram_range,
        length=args.histogram_length,
        mode=args.histogram_mode,
        decimals=args.histogram_decimals)
    rubik.set_dtype(args.dtype)


    help_done = False
    for key in dir(args):
        if key.startswith('help_') and getattr(args, key):
            help_function = getattr(help_functions, key)
            help_function()
            help_done = True
    if help_done:
        return 0
        
    
    if args.random_seed is not None:
        set_random_seed(args.random_seed)

    if args.visualizer_list:
        from ..visualizer import list_controllers, list_visualizers
        list_controllers(logger)
        list_visualizers(logger)
        return 0

    return_code = 0
    try:
        return_code = rubik.run()
    except RubikMemoryError:
        log.trace_error()
        logger.error("error: the memory limit of {0} has been exceeded; you can try to increase the memory limit (--memory-limit/-m)".format(args.memory_limit))
    except RubikExpressionError as err:
        log.trace_error()
        logger.error("\n=== expression error ===\n")
        log.trace_error(exc_info=err.expression_exception_info)
    except:
        log.trace_error()

    return return_code

