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

import os
import sys
import shutil
import argparse
import subprocess

from rubik import conf
from rubik import utils
from rubik.application import log as rubik_log

from . import log
from ..rubik_test_main import RubikTestMain

AVAILABLE_COVERAGE_TOOLS = ('python-coverage', 'coverage')
DEFAULT_COVERAGE_TOOL = 'coverage'

def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]

    description = """\
================================================================================
Rubik testing system {version}
================================================================================
This is the command line interface to the rubik testing system.

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

#    parser.add_argument("--trace-errors", "-E",
#        dest="trace_errors",
#        action="store_true",
#        default=False,
#        help="show error traceback")

    parser.add_argument("--list", "-l",
        dest="list",
        action="store_true",
        default=False,
        help="list available tests")

    parser.add_argument("--coverage", "-c",
        dest="coverage",
        action="store_true",
        default=False,
        help="run coverage tool")

    parser.add_argument("--coverage-tool", "-Ct",
        dest="coverage_tool",
        choices=AVAILABLE_COVERAGE_TOOLS,
        default=DEFAULT_COVERAGE_TOOL,
        help="set coverage tool")

    parser.add_argument("--coverage-htmldir", "-Ch",
        dest="coverage_htmldir",
        type=str,
        default="coverage_htmldir",
        help="set coverage html dir")

    parser.add_argument("--warnings", "-W",
        action="append",
        choices=conf.ALL_WARNINGS,
        default=[],
        help="enable warnings")

    parser.add_argument("--dry-run", "-d",
        dest="dry_run",
        action="store_true",
        default=False,
        help="dry run (do not run tests)")

    parser.add_argument("--version",
        action="version",
        version='{program} {version}'.format(program=conf.PROGRAM_NAME, version=conf.VERSION))

    parser.add_argument("test_patterns",
        type=str,
        nargs='*',
        help="add a test pattern; if preceded by ! or ^, skip matching tests; if no patterns are specified, the default is '*'")

    try:
        args = parser.parse_args(arguments)
    except Exception as err:
        sys.stderr.write("error: {0}: {1}\n".format(err.__class__.__name__, err))
        return 1

    conf.enable_warnings(*args.warnings)
    PRINT = rubik_log.PRINT

    # test
    test_logger = log.set_test_logger(args.verbose_level)

    if args.coverage: # pragma: no cover
        coverage_htmldir = os.path.abspath(args.coverage_htmldir)
        if os.path.exists(coverage_htmldir):
            shutil.rmtree(coverage_htmldir)
        if args.coverage_tool == "coverage":
            coverage_tool = "coverage"
            coverage_tool_args = ["--source", "rubik,rubik.application,rubik.application.help_functions,rubik.cubes"]
        elif args.coverage_tool == "python-coverage":
            coverage_tool = "coverage"
            coverage_tool_args = []
        if coverage_tool == "coverage":
            omit_args = ["--omit", "*/visualizer/*,*/tmp.*,*/tvtk/*,*/apptools/*,*/mayavi/*,*/vtk/*"]
            command_line = [args.coverage_tool, "run"]
            command_line.extend(omit_args)
            command_line.extend(coverage_tool_args)
            command_line.append(sys.argv[0])
            command_line.append("--verbose-level={}".format(args.verbose_level))
            command_line.extend(repr(p) for p in args.test_patterns)

            test_logger.warning("running coverage tool {}...".format(args.coverage_tool))
            test_logger.warning("running command {}...".format(' '.join(repr(e) for e in command_line)))
            p = subprocess.Popen(command_line)
            output, error = p.communicate()
            if p.returncode != 0:
                test_logger.error("coverage run failed - exiting")
                sys.exit(p.returncode)
    
            command_line = [args.coverage_tool, "html", "--directory={}".format(coverage_htmldir)]
            command_line.extend(omit_args)
            test_logger.warning("running command {}...".format(' '.join(repr(e) for e in command_line)))
            p = subprocess.Popen(command_line)
            output, error = p.communicate()
            if p.returncode != 0:
                test_logger.error("coverage html failed - exiting")
                sys.exit(p.returncode)
        
            test_logger.warning("coverage htmldir is {}".format(coverage_htmldir))

    else:
        patterns = utils.flatten_list(args.test_patterns, depth=1)
        rubik_test_main = RubikTestMain(logger=test_logger, verbose_level=args.verbose_level)
        if args.list:
            for test_num, test_name in enumerate(rubik_test_main.filter_test_names(patterns)):
                PRINT("{:5d}) {}".format(test_num, test_name))
        if not args.dry_run:
            result = rubik_test_main.run(patterns)
            return_code = len(result.failures)
            return return_code
    return 0

