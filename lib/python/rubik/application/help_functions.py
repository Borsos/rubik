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

import sys
import numpy

from .log import PRINT
from .example import Example
from .tempdir import chtempdir
from .. import conf
from .. import cubes

__all__ = [
              'help_dtypes',
              'help_cubes',
              'help_numpy',
              'help_labeled_options',
              'help_expression',
              'help_extractor',
              'help_user_defined_variables',
              'help_split',
              'help_filenames',
              'help_environment_variables',
              'help_creating_cubes',
              'help_output',
              'help_memory_usage',
              'help_usage',
          ]

_DEMO_TEXT = """\
# Examples/recipes

## 1. Create a random cube with a given shape:

$ rubik -e 'cb.random_cube("8x10x20")' -o r_{shape}.{format}
$ echo ciao
ciao
$

This will create 'r_8x10x20.raw'.

<<<BREAK>>>
## 2. Create a cube with linear values:

$ rubik -e 'cb.linear_cube("8x10x20")' -o l_{shape}.{format}
$

<<<BREAK>>>
## 3. Read a cube and write it with a different format:

$ rubik -i r_{shape}.{format} -s 8x10x20 -o r.x -Of text
$

<<<BREAK>>>
## 4. Read a cube and write it with a different data type:

$ rubik -i r_{shape}.{format} -s 8x10x20 -o r_{shape}.{dtype}.{format} -Ot float64
$

This will read from 'r_8x10x20.raw' a float32 cube (float32 is the
default data type) and write it to r_8x10x20.float64.raw as float64

<<<BREAK>>>
## 5. Read a subcube consisting of the \
      full x and z dimension, and of \
      indices from third to third to last along y, and write it:

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,2:-2,: \\
        -o rsub_{shape}.{format} -v
reading 960 'float32' elements (3840 bytes) from 'raw' file 'r_8x10x20.raw'[:, 2:-2, :]...
writing 960 'float32' elements (3840 bytes) to 'raw' file 'rsub_8x6x20.raw'...
$

<<<BREAK>>>
## 6. Read a subcube, subsample it along y and z dimension:

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,::2,::4 \\
        -o rsub_{shape}.{format} -v
reading 200 'float32' elements (800 bytes) from 'raw' file 'r_8x10x20.raw'[:, ::2, ::4]...
writing 200 'float32' elements (800 bytes) to 'raw' file 'rsub_8x5x5.raw'...
$

<<<BREAK>>>
## 7. Read a 3D cube, extract a 2D plane corresponding to y=5:

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,5,: \\
        -o rsub_{shape}.{format} -v
reading 160 'float32' elements (640 bytes) from 'raw' file 'r_8x10x20.raw'[:, 5, :]...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_8x20.raw'...
$

<<<BREAK>>>
## 8. Read a 3D cube, subsample on y, extract a 2D plane for each resulting y \
value (== split on the second dimension):

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,::2,: \\
        -o rsub_y{d1}_{shape}.{format} \\
        --split 1 -v
reading 800 'float32' elements (3200 bytes) from 'raw' file 'r_8x10x20.raw'[:, ::2, :]...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y0_8x20.raw'...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y1_8x20.raw'...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y2_8x20.raw'...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y3_8x20.raw'...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y4_8x20.raw'...
$

<<<BREAK>>>
### 9. Compute a linear combination of two input files:

$ rubik -i r_{shape}.{format} \\
        -i l_{shape}.{format} \\
        -s 8x10x20 \\
        -e '0.5 * i0 - i1 / 0.5' \\
        -o res0_{shape}.{format} -v
reading 1600 'float32' elements (6400 bytes) from 'raw' file 'r_8x10x20.raw'...
reading 1600 'float32' elements (6400 bytes) from 'raw' file 'l_8x10x20.raw'...
evaluating expression '0.5 * i0 - i1 / 0.5'...
writing 1600 'float32' elements (6400 bytes) to 'raw' file 'res0_8x10x20.raw'...
$

or:

$ rubik -i r_{shape}.{format} \\
        -i l_{shape}.{format} \\
        -s 8x10x20 \\
        -e f=0.5 \\
        -e 'f * i0 - i1 / f' \\
        -o res1_{shape}.{format} -v
reading 1600 'float32' elements (6400 bytes) from 'raw' file 'r_8x10x20.raw'...
reading 1600 'float32' elements (6400 bytes) from 'raw' file 'l_8x10x20.raw'...
evaluating expression 'f=0.5'...
evaluating expression 'f * i0 - i1 / f'...
writing 1600 'float32' elements (6400 bytes) to 'raw' file 'res1_8x10x20.raw'...
$

<<<BREAK>>>
### 10. Compute a linear combination with a portion of a file:

$ rubik -i r_{shape}.{format} -s 8x10x20 -x i0=:,4,: \\
        -i rsub_y2_{shape}.{format} -s 8x20 \\
        -e 'i1 - i0' \\
        -o rdiff_{shape}.{format} -v
reading 160 'float32' elements (640 bytes) from 'raw' file 'r_8x10x20.raw'[:, 4, :]...
reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y2_8x20.raw'...
evaluating expression 'i1 - i0'...
writing 160 'float32' elements (640 bytes) to 'raw' file 'rdiff_8x20.raw'...
$

<<<BREAK>>>
### 11. Show statistics about a cube:

$ rubik -i rdiff_8x20.raw -s 8x20 --stats
shape         = 8x20
#elements     = 160
min           = 0.0
max           = 0.0
sum           = 0.0
ave           = 0.0
#zero         = 160 [100.00%]
#nonzero      = 0 [0.00%]
#nan          = 0 [0.00%]
#inf          = 0 [0.00%]
$

<<<BREAK>>>
### 12. Check if two cubes are equal content within a given tolerance '1e-5':

$ rubik -i r_{shape}.{format} -s 8x10x20 -x i0=:,4,: \\
        -i rsub_y2_{shape}.{format} -s 8x20 \\
        -e 'cb.equals(i1, i0, 1e-5)' \\
        --print
True
$

<<<BREAK>>>
## 13. Print a random cube with integer values between -5 and +5:

$ rubik -e 'cb.random_cube("3x5", min=-5, max=5)' \\
        --dtype int32 \\
        --random-seed 100 \\
        --print
[[ 0 -2  0  3 -4]
 [-3  1  3 -3  0]
 [ 3 -2 -3 -3 -2]]
$

The '--random-seed 100' option sets the random seed; it has been added to make
the result reproducible.

<<<BREAK>>>
## 14. Setting a single value on a cube:
$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -e '_r[0, 0, 0] = 4' \\
        -o o_{shape}.{format}
$

The '_r' variable is the current result; in this case, the cube just read. In
this case, it is 'i0', but in general it can be the result of a previos
expression; for instance:

$ rubik -t int32 \\
        --random-seed 100 \\
        -e 'cb.random_cube("3x4x5", min=0.0, max=10.0)' \\
        -e '_r[:, 1, :] = -5' \\
        --print
[[[ 5  2  4  8  0]
  [-5 -5 -5 -5 -5]
  [ 8  2  1  1  2]
  [ 9  8  1  8  2]]

 [[ 4  9  8  3  1]
  [-5 -5 -5 -5 -5]
  [ 5  6  1  3  0]
  [ 8  9  0  8  5]]

 [[ 7  6  5  0  2]
  [-5 -5 -5 -5 -5]
  [ 9  8  3  5  3]
  [ 3  1  2  0  5]]]
$

<<<BREAK>>>
## 15. Setting multiple values on a cube:
$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -e '_r[0, :, 3] = 4' \\
        -o o_{shape}.{format}
$



"""
def help_cubes():
    help(cubes)

def help_numpy():
    help(numpy)

def help_expression():
    PRINT("""\
Generic expressions/source code
===============================
--------------------------------------------------------------------------------
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

Inside an expression/source you can access:
* the numpy module, as 'numpy' or 'np';
* the cubes module, as 'cubes' or 'cb';
* all the used defined variables (variables set in previous expressions);
* all the input cubes (by default 'i0', 'i1', ..., 'iN');
* the current result '_r' (which is generally a cube, but not necessarily).

The 'cubes' module provides some numpy-based functions to operate with
cubes; see --help-cubes.

Expressions starting with '-'
=============================
If an expression starts with a '-' sign, rubik can try to parse it as an
option:

$ rubik '-cb.linear_cube("3x4")' --print
usage: rubik [-h] [--verbose] [--version] [--trace-errors] [--safe]
             [--optimized] [--optimized-min-size S] [--memory-limit L[units]]
             [--dtype D] [--accept-bigger-raw-files] [--clobber]
             [--no-clobber] [--random-seed RANDOM_SEED]
             [--source-file E [E ...]] [--expression E [E ...]]
             [--input-filename I] [--shape [D0[:D1[...]]]] [--extract X]
             [--input-dtype D] [--input-format INPUT_FORMATS]
             [--input-csv-separator S] [--input-text-delimiter D]
             [--in-place | --output-filename O] [--print] [--stats]
             [--split D] [--output-dtype D] [--output-format OUTPUT_FORMATS]
             [--output-csv-separator S] [--output-text-delimiter D]
             [--output-text-newline N] [--output-text-converter C]
             [--help-dtypes] [--help-labeled-options] [--help-expression]
             [--help-extractor] [--help-user-defined-variables] [--help-numpy]
             [--help-cubes] [--help-filenames] [--help-split]
             [--help-environment-variables] [--help-creating-cubes]
             [--help-output] [--help-memory-usage] [--help-usage]
             [expression [expression ...]]
rubik: error: unrecognized arguments: -cb.linear_cube("3x4")

In this case, you can pass all the expressions positionally after '--':

$ rubik --print -- '-cb.linear_cube("3x4")'
[[ -0.  -1.  -2.  -3.]
 [ -4.  -5.  -6.  -7.]
 [ -8.  -9. -10. -11.]]

Other working alternatives are:

$ rubik --print -e'-cb.linear_cube("3x4")'
...
$ rubik --print -e='-cb.linear_cube("3x4")'
...
$ rubik --print --expression='-cb.linear_cube("3x4")'
...

or, more tricky:
$ rubik '0 - cb.linear_cube("3x4")' --print
...

Loading expressions from files
==============================
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

""")

def help_extractor():
    PRINT("""\
Extractors
==========
An extractor can be associated to each input file to read only a portion of that
file. Due to memory opimization, only the portion is read, so there is no need
to temporarily store the entire file. This means that if you want to read only a
subcube from a huge file, you will use memory only for the subcube.

Extractors are lists of index selectors separated by 'x' or ','.

Each input file can have a specific extractor. The shape and the extractor must
have the same rank.

Each index selector can be:
* a python slice [start:]stop[:step], for instance
  - ':' -> select all indices
  - '1:' -> select all indices but the first
  - ':-3' -> select all indices but the last three
  - '::2' -> select from the first to the last indices with stride 2
* an integer number; in this case, only the corresponding index is selected on
  that dimension, and the dimension is skipped in the output.

For instance, if the shape is '8x1000x30':
* '-x :x0x:' will extract the subcube '8x30' corresponding to the plane with 0
  on the second dimension
* '-x 3:x8:10x:5' will extract a subcube '5x2x5' (remember that, in a python
  slice, the start is always included and the stop is always excluded.
""")

def help_user_defined_variables():
    PRINT("""\
User defined variables
======================
It is possible to use expressions to set variables; this variables can then
be used in the following expressions. For instance:

$ rubik -i l_{shape}.{format} \\
        -i r_{shape}.{format} \\
        -s 8x10 \\
        -e alpha=1.5 \\
        -e beta=-0.5 \\
        -e 'alpha * i0 + beta * i1' \\
        -o o_{shape}.{format}
""")

def help_dtypes():
    PRINT("""\
Available data types
====================
All numpy dtypes are valid data types.
You can set:
* the internal dtype, which is the default dtype;
* the specific dtype for each input file ('--input-dtype/-It');
* the specific dtype for each output file ('--output-dtype/-Ot');

This is the list of the available numpy dtypes:
""")
    for dtype_name, dtype_description in conf.DATA_TYPES.items():
        PRINT("{n:16s} {d}".format(n=dtype_name, d=dtype_description))

def help_labeled_options():
    PRINT("""\
Labeled options
===============
--------------------------------------------------------------------------------
Labeled options are options whose value can be preceded by a label assignment.

There are two kind of labeled options:
* input labeled options, referring to input files, and
* output labeled options, referring to output files.

For instance, '--shape/-s' is an input labeled option. It can be used:
* unlabeled: '--shape 8x10'
* labeled: '--shape i0=8x10'

When used unlabeled, the shape will apply to all the input filenames that do not
have a labeled shape option.
On the other hand, when used labeled, it applies only to the input filename that
has the same label.
If multiple unlabeled --shape/-s options are passed, they are applied to the
corresponding input files: the first unlabeled option to the first input file,
the second unlabeled option to the second file, and so on.

For instance:

* 'rubik -i a.raw -i b.raw -c i.raw -s 8x10 ...': the shape 8x10 is assigned to
  all the input files.
* 'rubik -i a.raw -i b.raw -c i.raw -s 8x10 -s i1=8x20x10 ...': the shape 8x10
  is assigned to 'a.raw' and 'c.raw', since 'b.raw' has a labeled shape option, so
  its shape is 8x20x10;
* 'rubik -i a.raw -i b.raw -c i.raw -s 8x10 -s 8x20x10 ...': in this case,
  - 'a.raw' has shape 8x10;
  - 'b.raw' and 'c.raw' have shape 8x20x10.

The same applies to output labeled options.
""")

def help_split():
    PRINT("""\
Splitting dimensions
====================
Suppose you have a _8x4x10_ cube, and you want to write _4_ _8x10_ cubes, one
for each index in the second dimension. The command is:

$ rubik -i a_{shape}.{format} -s 8x4x10 --split 1 -o s_{shape}.{d1}.{format} -v
reading 320 'float32' elements (1280 bytes) from 'raw' file 'a_8x4x10.raw'...
writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.0.raw'...
writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.1.raw'...
writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.2.raw'...
writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.3.raw'...
$

During the output phase, a loop over the four values for the second index is
done; the 3-D cube is sliced across the second dimension, and each plane
is saved into a different file.

The 'd1' key has been added to the available keys for the output filename
interpolation.

""")

def help_filenames():
    PRINT("""\
Input filenames
===============
For each input filename, a label 'i<N>' is generated referring to the cube
read from this file; 'N' is the ordinal of the input filename.

For instance, 'i0' refers to the cube read from the first file, 'i1' to the cube
read from the second file, and so on.

These labels can be used to
* set specific parameters for each input file, like:
  - the format
  - the dtype
  - the shape
  - an extractor
  for instance, '-s i0=8x10' sets the shape for the first input cube only;
* refer to the corresponding cube in expressions; in this case, 'i0' refers to
  the cube read from the first input filename, after the extractor has been
  applied (indeed extractors are applied just during the file loading).

See --help-labeled-options/-ho for more information about options referring to
labeled files.

You can change the name of the label referring to a cube; simply put the
label before the filename, separated by '=': so, the option '-i a=a_8x10.raw'
will associate the read cube to the label 'a'; then, '-x a=:2x2:' sets an 
extractor for the file 'a_8x10.raw' only, and '-e "2.5 * a"' multiplies
the cube extracted from 'a_8x10.raw' by 2.5.

Output filenames
================
Also the output filenames have a label (by default 'o0'); the label can be used
to set specific parameters on the output file, for instance the format. It
cannot be used in expressions.

For instance, '-o x=x_8x10.raw --output-dtype x=float64' applies the dtype
'float64' to the output file 'x_8x10.raw'.

Filename interpolation
======================
Filenames are interpolated; the following keywords are substituted:
* shape: the cube shape, for instance '3x2x4';
* rank: the cube shape rank, for instance '3' if the shape is '3x2x4';
* count: the number of elements, for instance '2x4';
* dtype: the data type, for instance 'float32';
* format: the file format ({ff})

For instance, 'a_{{shape}}.{{format}}' is converted to 'a_3x2x4.raw' if shape
is '3x2x4' and file format is 'raw'.

This allows to specify the same filename as input and output, and still have
the output on separate files. For instance,
  -i a_{{shape}}.{{format}} -Oi -s 8x10 -If raw -Of text -Oc '%.4e'
will read 'a_8x10.raw' and write 'a_8x10.text'.

File formats
============
Three file formats are available:
* 'raw' is the default, for binary files; they are not portable across different
  platforms;
* 'text' is for text files; they have sub-options:
  - delimiter (usually a space) separating values in a row;
  - newline (usually '\\n') separating rows;
  - converter (for instance '%.18e') is the format specifier for values.
  for input files only the 'delimiter' can be set;
* 'csv' is for text files consisting of values separated by a separator; you can
  set
  - separator (by default ',') the separator between values.
""".format(ff='|'.join(conf.FILE_FORMATS)))

def help_environment_variables():
    PRINT("""\
    Environment variables
=====================
Currently the only accepted environment variable is '$RUBIK_OPTIONS', that can
be set to a list of valid rubik options. For instance:

$ export RUBIK_OPTIONS='-v --memory-limit 16gb'

These options will be prepended to the list of command line arguments. So, they
can be overwritten by command line arguments.
""")

def help_creating_cubes():
    PRINT("""\
Creating cubes from scratch
===========================
It is possible to create cubes from scratch, using an expression.  For instance:

$ rubik -e 'np.linspace(0, 79, 80).reshape((8, 10))' -o lc_{shape}.{format}

will create a cube with values from 0.0 to 79.0 with increment 1.0.

The cubes (or cb) module has some convenience functions to easily
create cubes:

$ rubik -e 'cb.linear_cube("8x10")' -o lc_{shape}.{format}

creates the same cube;

$ rubik -e 'cb.random_cube("8x10")' -o rc_{shape}.{format}

creates a random cube; and

$ rubik -e 'cb.const_cube("8x10", 8.0)' -o cc_{shape}.{format}

creates a const cube with all values 8.0.

$ rubik -e 'cb.const_blocks_cube("8x10x4", start=0.0, increment=1.0, const_dims=[1, 2])' \\
        -o cc_{shape}.{format}

creates a cube _r for which each subcube _r[x, :, :] is const, with value 'x'.
In general, if the cube is N-dimensional, every subcube obtained by fixing
all the coordinates except those listed in const_dims (d_a, d_b, d_c, ...) has
const values. Moreover, the first subcube corresponding to (0, 0, ..., 0) has
value 'start', the second, corresponding to (0, 0, ..., 1) has value 'start + 
increment', and so on.

See --help-cubes to see the content of the cubes module.
""")

def help_output():
    PRINT("""\
Output modes
============
There are three output modes:
* writing the result to a file (--output-filename/-o); you can specify the file
  format, dtype, etc...
* print the result to a file (--print/-P)
* print statistics about the resulting cube to a file (--stats/-S)
""")

def help_memory_usage():
    PRINT("""\
Memory usage
============
A complete control of the memory usage is not possible, due to the possibility
to execute generic expressions involving numpy arrays. Nevertheless rubik can
check the amount of memory necessary to read input files and store the result.
You can provide a limit for this amout of memory using the '--memory-limit/m'
option.

For instance, with the option '--memory-limit 16gb', you will not allowed to
read more than 16 gb of data. The default memory limit is '0', which means no
limit.

Optimized read vs Safe read
===========================
When loading input files, two algorithms are available:
* optimized read
* safe read
The optimized read is memory efficient: if an extractor is used, it is applied
directly during the read, so only the exact amount of memory to store the
subcube is used. On the other hand, the safe read reads the full cube, and
then applies the extractor in memory.

The two algorithms are fully equivalent, but the safe one can do some more
checks (for instance, if the file format is 'text' or 'csv', the optimized
algorithm is not able to check if the input file is bigger than the specified
shape).

The safe algorithm is used when the extractor is missing, or when the
extracted subcube has the same size as the input cube. Moreover, the safe
algorithm is used if the size of the input cube is lower than a limit that
can be set through the '--optimized-min-size' option. For instance, if
'--optimized-min-size 1gb', the safe algorithm is always used if the input
file is less than 1gb. By default, the optimized min size is 100mb.
""")

def help_usage():
    with chtempdir():
        example = Example(_DEMO_TEXT)
        example.show(test=True, interactive=False)

def help_demo():
    with chtempdir():
        example = Example(_DEMO_TEXT)
        example.show(test=True, interactive=True)