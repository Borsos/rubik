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

import argparse
import glob
import os
import sys

from rubik import conf
from rubik.application import log as rubik_log
from rubik.application.help_functions.example import Example
from rubik.application.tempdir import chtempdir

from . import log

def iterfilenames(patterns):
    for filename_pattern in patterns:
        for filename in glob.glob(filename_pattern):
            if os.path.isfile(filename):
                yield filename
            
def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]

    description = """\
================================================================================
Rubik example testing system {version}
================================================================================
This tool can be used to validate rubik examples, such as wiki md files.

""".format(version=conf.VERSION)
    epilog = ""
    
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--verbose", "-v",
        dest="verbose_level",
        action="count",
        default=1,
        help="increase verbose level")

    parser.add_argument("--verbose-level",
        metavar="VL",
        dest="verbose_level",
        type=int,
        default=1,
        help="set verbose level")

    parser.add_argument("--quiet", "--silent", "-q",
        dest="verbose_level",
        action="store_const",
        const=0,
        default=0,
        help="set quiet mode (warning messages are disabled)")

    parser.add_argument("--trace-errors", "-E",
        dest="trace_errors",
        action="store_true",
        default=False,
        help="show error traceback")

    parser.add_argument("--list", "-l",
        dest="list",
        action="store_true",
        default=False,
        help="list selected examples")

    parser.add_argument("--dry-run", "-d",
        dest="dry_run",
        action="store_true",
        default=False,
        help="dry run (do not validate examples)")

    parser.add_argument("--warnings", "-W",
        action="append",
        choices=conf.ALL_WARNINGS,
        default=[],
        help="enable warnings")

    parser.add_argument("--version",
        action="version",
        version='{program} {version}'.format(program=conf.PROGRAM_NAME, version=conf.VERSION))

    parser.add_argument("filenames",
        type=str,
        nargs='*',
        help="pattern matching example files, for instance '*.md'")

    try:
        args = parser.parse_args(arguments)
    except Exception as err:
        sys.stderr.write("error: {0}: {1}\n".format(err.__class__.__name__, err))
        return 1

    conf.enable_warnings(*args.warnings)
    PRINT = rubik_log.PRINT

    # test
    test_logger = log.set_test_logger(args.verbose_level)

    for c, filename in enumerate(iterfilenames(args.filenames)):
        if args.list:
            test_logger.info("{:8d}) {}".format(c, filename))
        if not args.dry_run:
            with open(filename, "rb") as f_in:
                text = f_in.read()
            example = Example(text=text)
            with chtempdir(prefix="tmp.ex.", dir=os.getcwd()) as temp_dir_info:
                try:
                    example.show(test=True)
                except Exception as err:
                    rubik_log.trace_error(args.trace_errors)
                    temp_dir_info.clear = False
                    test_logger.warning("example file {} failed - leaving test dir {}".format(filename, temp_dir_info.dirname))
                    return 1
    return 0

