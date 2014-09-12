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

__all__ = [
              'HelpExpression',
              'help_expression',
          ]

from .functor_help_example import HelpExample

def help_expression(test=None, interactive=None, writer=None):
    HelpExpression(test=test, interactive=interactive, writer=writer)()

class HelpExpression(HelpExample):
    TEXT = """\
# Generic expressions/source code

You can pass to rubik generic python source code to be executed. This source
code can be:

* a python 'eval' expression producing a value, like '0.5 * i0 - 0.5 * i1' (this
  will set '_r', the current result, to the value produced by the expression);

* a python 'exec' source, like '_r[1, :] = 3.0' (this will set to 3.0 all the
  points having first coordinate == 1 in '_r', which should be a 2D cube in this
  case).

Expressions/source can be passed:

* positionally, for instance

  $ rubik 'cb.linear_cube("4x4")' --print

* through the '--expression/-e' option:

  $ rubik -e 'cb.linear_cube("4x4")' --print

* through the '--source-file/-f' option, that :

  $ rubik -f expr.txt --print

  in this case, 'expr.txt' must be an existing file containing valid source
  code;

* passing an expression starting with '@', for instance

  $ rubik @expr.txt --print

  which is equivalent to 'rubik -f expr.txt --print'.

You can pass multiple expressions/source files; they will be evaluated in order.

<<<BREAK>>>

Inside an expression/source you can access:
* the numpy module, as 'numpy' or 'np';
* the cubes module, as 'cubes' or 'cb';
* all the used defined variables (variables set in previous expressions);
* all the input cubes (by default 'i0', 'i1', ..., 'iN');
* the list of the input cubes '_i';
* the current result '_r' (which is generally a cube, but not necessarily).
* input/output functions

The 'cubes' module provides some numpy-based functions to operate with
cubes; see --help-cubes.

## Input functions

It is possible to read input files by using the following function:
* read_cube(filename=None, label=None, shape=None, extractor=None, mode=None, offset=None, dtype=None, format=None, csv_separator=None, text_delimiter=None)
  This is automatically set by '--input-filename/-i' option (and related
  input labeled options)

## Output functions

It is possible to print/view the results using the following functions:
* write_cube(filename=None, label=None, cube=None, mode=None, offset=None, dtype=None, format=None, csv_separator=None, text_delimiter=None, text_newline=None, text_converter=None)
  This is automatically set by '--output-filename/-o' option (and related
  output labeled options)
* print_cube()
  This is automatically set by '--print/-P' option
* print_stats()
  This is automatically set by '--stats/-S' option
* compare_stats()
  This is automatically set by '--compare-stats/-C' option
* diff()
  This is automatically set by '--diff/-D' option
* print_histogram(cube=None, bins=None, hrange=None, decimals=None, fmt=None)
  This is automatically set by '--histogram/-H' option (and related
  histogram options)
* view(cube=None, visualizer_type=None, title=None)
  This is automatically set by '--view/-V' option (and related
  visualizer options)

## Expressions starting with '-'

If an expression starts with a '-' sign, rubik can try to parse it as an
option:

$ rubik '-cb.linear_cube("2x4")' --print
usage: rubik [--verbose] [--verbose-level VL] [--quiet] [--report] [--dry-run]
             [--version] [--logo] [--trace-errors] [--read-threshold-size S]
             [--memory-limit L[units]] [--dtype D] [--accept-bigger-raw-files]
             [--clobber] [--no-clobber] [--random-seed RANDOM_SEED]
             [--warnings {RuntimeWarning,all}] [--source-file E [E ...]]
             [--expression E [E ...]] [--test] [--input-filename I [I ...]]
             [--shape [D0[:D1[...]]]] [--extract X] [--input-mode INPUT_MODES]
             [--input-offset INPUT_OFFSETS] [--input-dtype D]
             [--input-format INPUT_FORMATS] [--input-csv-separator S]
             [--input-text-delimiter D] [--output-filename O [O ...]]
             [--print-cube] [--print-stats] [--compare-stats] [--diff]
             [--histogram] [--view] [--histogram-bins Hb]
             [--histogram-range Hr Hr] [--histogram-decimals Hd]
             [--histogram-length Hl] [--histogram-percentage]
             [--histogram-num] [--view-volume-slicer] [--view-auto]
             [--view-attribute VA [VA ...]] [--view-attribute-file VF]
             [--view-list] [--split D] [--output-mode Om] [--output-offset Oo]
             [--output-dtype D] [--output-format Of]
             [--output-csv-separator S] [--output-text-delimiter D]
             [--output-text-newline N] [--output-text-converter C]
             [--test-pattern SP[.TP] [SP[.TP] ...]] [--test-list]
             [--test-verbose] [--test-verbose-level TEST_VERBOSE_LEVEL]
             [--help] [--usage] [--help-dtypes] [--help-labeled-options]
             [--help-expression] [--help-extractor]
             [--help-user-defined-variables] [--help-numpy] [--help-cubes]
             [--help-filenames] [--help-split] [--help-environment-variables]
             [--help-creating-cubes] [--help-output] [--help-memory-usage]
             [--help-usage] [--demo]
             [expression [expression ...]]
rubik: error: unrecognized arguments: -cb.linear_cube("2x4")
$

In this case, there are some alternatives:

$ rubik -e'-cb.linear_cube("2x4")' --print
[[-0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$ rubik -e='-cb.linear_cube("2x4")' --print
[[-0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$ rubik -e='-cb.linear_cube("2x4")' --print
[[-0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$ rubik --expression='-cb.linear_cube("2x4")' --print
[[-0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$ rubik '0 - cb.linear_cube("2x4")' --print
[[ 0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$

It is also possible to use the '--' option to mark the end of options; 
nevertheless, in this case the '--print' option will not be recognized,
so the 'print_cube()' function must be called instead:

$ rubik -- '-cb.linear_cube("2x4")' 'print_cube()'
[[-0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$

or also

$ rubik 'print_cube(-cb.linear_cube("2x4"))'
[[-0. -1. -2. -3.]
 [-4. -5. -6. -7.]]
$

In the latter case, the '--' option is not necessary, since the expression
does not start with '-'.

## Loading expressions from files

It is possible to load expressions from file; for instance:

$ cat expr.txt
a = cb.linear_cube("3x4")
a[1, :] += 10
a[:, 1] -= 10
_r = a + 0.5
$ rubik -f expr.txt --print
[[  0.5  -8.5   2.5   3.5]
 [ 14.5   5.5  16.5  17.5]
 [  8.5  -0.5  10.5  11.5]]
$

If an expression starts with '@', it is considered a filename to be load. For
instance:

$ rubik @expr.txt --print
[[  0.5  -8.5   2.5   3.5]
 [ 14.5   5.5  16.5  17.5]
 [  8.5  -0.5  10.5  11.5]]
$

"""

    def setUp(self):
        with open("expr.txt", "w") as f_out:
            f_out.write("""\
a = cb.linear_cube("3x4")
a[1, :] += 10
a[:, 1] -= 10
_r = a + 0.5
""")

