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

import sys
import numpy

from .log import PRINT
from .. import conf
from .. import cubist_numpy

__all__ = [
              'help_dtypes',
              'help_cubist_numpy',
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

def help_cubist_numpy():
    help(cubist_numpy)

def help_numpy():
    help(numpy)

def help_expression():
    PRINT("""\
Generic numpy expressions
=========================
The --expression/-e options allows to pass a generic numpy expression to be
evaluated. The input cubes are available through the labels referring to them.

From the expression you can access:
* the numpy module, as 'numpy' or 'np';
* the cubist_numpy module, as 'cubist_numpy' or 'cnp';
* all the used defined variables.

The cubist_numpy module provides some numpy-based functions to operate with
cubes; see --help-cubist-numpy.
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
User defined variables can be used in generic numpy expressions. For instance:
  -V alpha=1.5 -V beta=-0.5 -e 'alpha * i0 + beta * i1'
is equivalent to 
  -e '1.5 * i0 - 0.5 * i1'
Also input cubes and previusly defined variables can be used:
  -V a=10 -V b='a + 5' -V c='i0 * b'
will set
  * a = 10
  * b = 15
  * c = i0 * 15 ('i0' is the first cube)
""")

def help_dtypes():
    PRINT("""\
Available dtypes
================
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

* 'cubist -i a.raw -i b.raw -c i.raw -s 8x10 ...': the shape 8x10 is assigned to
  all the input files.
* 'cubist -i a.raw -i b.raw -c i.raw -s 8x10 -s i1=8x20x10 ...': the shape 8x10
  is assigned to 'a.raw' and 'c.raw', since 'b.raw' has a labeled shape option, so
  its shape is 8x20x10;
* 'cubist -i a.raw -i b.raw -c i.raw -s 8x10 -s 8x20x10 ...': in this case,
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

$ cubist -i a_{shape}.{format} -s 8x4x10 --split 1 -o s_{shape}.{d1}.{format} -v
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
* refer to the corresponding cube in a generic numpy expression; in this case,
  'i0' refers to the cube read from the first input filename, after the
  extractor has been applied (indeed extractors are applied just during the
  file loading).

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
cannot be used in the generic numpy expression.

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
Currently the only accepted environment variable is '$CUBIST_OPTIONS', that can
be set to a list of valid cubist options. For instance:

$ export CUBIST_OPTIONS='-v --memory-limit 16gb'

These options will be prepended to the list of command line arguments. So, they
can be overwritten by command line arguments.
""")

def help_creating_cubes():
    PRINT("""\
Creating cubes from scratch
===========================
It is possible to create cubes from scratch. Indeed, it is possible to use a
generic numpy expression without input filenames.

For instance:

$ cubist -e 'np.linspace(0, 79, 80).reshape((8, 10))' -o lc_{shape}.{format}

will create a cube with values from 0.0 to 79.0 with increment 1.0.

The cubist_numpy (or cnp) module has some convenience functions to easily
create cubes:

$ cubist -e 'cnp.linear_cube("8x10")' -o lc_{shape}.{format}

creates the same cube;

$ cubist -e 'cnp.random_cube("8x10")' -o rc_{shape}.{format}

creates a random cube; and

$ cubist -e 'cnp.const_cube("8x10", 8.0)' -o cc_{shape}.{format}

creates a const cube with all values 8.0.

$ cubist -e 'cnp.const_blocks_cube("8x10x4", start=0.0, increment=1.0, block_dims=2, start_dim=None)' \
         -o cc_{shape}.{format}

creates a cube of 8 10x4 const blocks, each block fill value is linearly
assigned starting from 'start' with increment 'increment'.  You can change the
block dimension and the starting dimension.

See --help-cubist-numpy to see the content of the cubist_numpy module.
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
to execute generic numpy expressions. Nevertheless cubist can check the amount
of memory necessary to read input files and store the result. You can provide
a limit for this amout of memory using the '--memory-limit/m' option.

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
    PRINT("""\
Examples/recipes
================

## 1. Create a random cube with a given shape:

$ cubist -e 'cnp.random_cube("8x10x20") -o r_{shape}.{format}

This will create 'r_8x10x20.raw'.

## 2. Create a cube with linear values:

$ cubist -e 'cnp.linear_cube("8x10x20") -o l_{shape}.{format}

## 3. Read a cube and write it with a different format:

$ cubist -i r_{shape}.{format} -s 8x10x20 -o r.x -Of text

## 4. Read a cube and write it with a different data type:

$ cubist -i r_{shape}.{format} -s 8x10x20 -o r_{shape}.{dtype}.{format} -Ot float64

This will read from 'r_8x10x20.raw' a float32 cube (float32 is the
default data type) and write it to r_8x10x20.float64.raw as float64

## 5. Read a subcube consisting of the full x and z dimension, and of
      indices from third to third to last along y, and write it:

$ cubist -i r_{shape}.{format} -s 8x10x20 \
         -x :,2:-2,: \
         -o rsub_{shape}.{format} -v
reading 1600 'float32' elements (6400 bytes) from 'raw' file 'r_8x10x20.raw'...
writing 960 'float32' elements (3840 bytes) to 'raw' file 'rsub_8x6x20.raw'...

## 6. Read a subcube, subsample it along y and z dimension:

$ cubist -i r_{shape}.{format} -s 8x10x20 \
         -x :,::2,::4 \
         -o rsub_{shape}.{format} -v
reading 1600 'float32' elements (6400 bytes) from 'raw' file 'r_8x10x20.raw'...
writing 200 'float32' elements (800 bytes) to 'raw' file 'rsub_8x5x5.raw'...

""")
