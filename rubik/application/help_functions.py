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

$ rubik -r 100 -e 'cb.random_cube("8x10x20")' -o r_{shape}.{format}
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
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 960 'float32' elements (3840 bytes) from 'raw' file 'r_8x10x20.raw'[:,2:-2,:]...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 960 'float32' elements (3840 bytes) to 'raw' file 'rsub_8x6x20.raw'...
$

<<<BREAK>>>
## 6. Read a subcube, subsample it along y and z dimension:

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,::2,::4 \\
        -o rsub_{shape}.{format} -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 200 'float32' elements (800 bytes) from 'raw' file 'r_8x10x20.raw'[:,::2,::4]...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 200 'float32' elements (800 bytes) to 'raw' file 'rsub_8x5x5.raw'...
$

<<<BREAK>>>
## 7. Read a 3D cube, extract a 2D plane corresponding to y=5:

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,5,: \\
        -o rsub_{shape}.{format} -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'r_8x10x20.raw'[:,5,:]...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_8x20.raw'...
$

<<<BREAK>>>
## 8. Read a 3D cube, subsample on y, extract a 2D plane for each resulting y \
value (== split on the second dimension):

$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -x :,::2,: \\
        -o rsub_y{d1}_{shape}.{format} \\
        --split 1 -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 800 'float32' elements (3200 bytes) from 'raw' file 'r_8x10x20.raw'[:,::2,:]...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y0_8x20.raw'...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y1_8x20.raw'...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y2_8x20.raw'...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y3_8x20.raw'...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rsub_y4_8x20.raw'...
$

<<<BREAK>>>
### 9. Join two or more files

$ rubik -i rsub_y0_{shape}.raw \
        -i rsub_y1_{shape}.raw \
        -i rsub_y2_{shape}.raw \
        -i rsub_y3_{shape}.raw \
        -i rsub_y4_{shape}.raw \
        -s 8x20 \
        'cb.join(_i)' \
        -o rj.{shape}.raw \
        -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y0_8x20.raw'...
rubik: evaluating expression "read_cube(label='i1')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y1_8x20.raw'...
rubik: evaluating expression "read_cube(label='i2')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y2_8x20.raw'...
rubik: evaluating expression "read_cube(label='i3')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y3_8x20.raw'...
rubik: evaluating expression "read_cube(label='i4')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y4_8x20.raw'...
rubik: evaluating expression 'cb.join(_i)'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 800 'float32' elements (3200 bytes) to 'raw' file 'rj.5x8x20.raw'...
$

<<<BREAK>>>
### 10. Compute a linear combination of two input files:

$ rubik -i r_{shape}.{format} \\
        -i l_{shape}.{format} \\
        -s 8x10x20 \\
        -e '0.5 * i0 - i1 / 0.5' \\
        -o res0_{shape}.{format} -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 1600 'float32' elements (6400 bytes) from 'raw' file 'r_8x10x20.raw'...
rubik: evaluating expression "read_cube(label='i1')"...
rubik: reading 1600 'float32' elements (6400 bytes) from 'raw' file 'l_8x10x20.raw'...
rubik: evaluating expression '0.5 * i0 - i1 / 0.5'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 1600 'float32' elements (6400 bytes) to 'raw' file 'res0_8x10x20.raw'...
$

or:

$ rubik -i r_{shape}.{format} \\
        -i l_{shape}.{format} \\
        -s 8x10x20 \\
        -e f=0.5 \\
        -e 'f * i0 - i1 / f' \\
        -o res1_{shape}.{format} -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 1600 'float32' elements (6400 bytes) from 'raw' file 'r_8x10x20.raw'...
rubik: evaluating expression "read_cube(label='i1')"...
rubik: reading 1600 'float32' elements (6400 bytes) from 'raw' file 'l_8x10x20.raw'...
rubik: evaluating expression 'f=0.5'...
rubik: evaluating expression 'f * i0 - i1 / f'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 1600 'float32' elements (6400 bytes) to 'raw' file 'res1_8x10x20.raw'...
$

<<<BREAK>>>
### 11. Compute a linear combination with a portion of a file:

$ rubik -i r_{shape}.{format} -s 8x10x20 -x i0=:,4,: \\
        -i rsub_y2_{shape}.{format} -s 8x20 \\
        -e 'i1 - i0' \\
        -o rdiff_{shape}.{format} -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'r_8x10x20.raw'[:,4,:]...
rubik: evaluating expression "read_cube(label='i1')"...
rubik: reading 160 'float32' elements (640 bytes) from 'raw' file 'rsub_y2_8x20.raw'...
rubik: evaluating expression 'i1 - i0'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 160 'float32' elements (640 bytes) to 'raw' file 'rdiff_8x20.raw'...
$

<<<BREAK>>>
### 12. Show statistics about a cube:

$ rubik -i rsub_y2_8x20.raw -s 8x20 --stats
shape     = 8x20
#elements = 160
%elements = 100.00%
min       = 0.017823184
min_index = (1, 10)
max       = 0.99523103
max_index = (5, 18)
sum       = 79.374161
ave       = 0.496089
#zero     = 0
%zero     = 0.00%
#nonzero  = 160
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
$

<<<BREAK>>>
### 13. Show statistics about many cubes:

In order to compare statistics about many cubes, the '--compare-stats/-C'
option can be used; in this case, a single report is shown for all the
compared cubes:

$ rubik -r 100 -e 'cb.random_cube("6x9x32")' -C \\
               -e 'cb.random_cube("6x9x32")' -C \\
               -e 'cb.random_cube("6x18x33")' -C
shape     = 6x9x32        6x9x32        6x18x33
#elements = 1728          1728          3564
%elements = 100.00%       100.00%       100.00%
min       = 0.00048675947 1.4618569e-05 1.7200797e-05
min_index = (1, 3, 13)    (1, 1, 13)    (1, 17, 0)
max       = 0.99947917    0.99867839    0.99991566
max_index = (2, 0, 11)    (0, 5, 20)    (5, 6, 8)
sum       = 842.42566     860.05499     1801.826
ave       = 0.487515      0.497717      0.505563
#zero     = 0             0             0
%zero     = 0.00%         0.00%         0.00%
#nonzero  = 1728          1728          3564
%nonzero  = 100.00%       100.00%       100.00%
#nan      = 0             0             0
%nan      = 0.00%         0.00%         0.00%
#inf      = 0             0             0
%inf      = 0.00%         0.00%         0.00%
$

<<<BREAK>>>
### 14. Show statistics about differences between two cubes:

The '--diff/-D' option allows to show statistics about the difference of
exactly two cubes. Statistics info is shown for
* left-hand cube
* right-hand cube
* relative difference
* absolute difference

$ rubik -r 100 -e 'cb.random_cube("6x9x32")' -D \\
               -e 'cb.random_cube("6x9x32")' -D
name      = LEFT          RIGHT         REL_DIFF      ABS_DIFF
shape     = 6x9x32        6x9x32        6x9x32        6x9x32
#elements = 1728          1728          1728          1728
%elements = 100.00%       100.00%       100.00%       100.00%
min       = 0.00048675947 1.4618569e-05 0.00038759335 0.00025051832
min_index = (1, 3, 13)    (1, 1, 13)    (4, 5, 19)    (4, 5, 19)
max       = 0.99947917    0.99867839    402.01849     0.98762667
max_index = (2, 0, 11)    (0, 5, 20)    (0, 3, 27)    (3, 3, 4)
sum       = 842.42566     860.05499     5523.7295     588.99091
ave       = 0.487515      0.497717      3.1966        0.340851
#zero     = 0             0             0             0
%zero     = 0.00%         0.00%         0.00%         0.00%
#nonzero  = 1728          1728          1728          1728
%nonzero  = 100.00%       100.00%       100.00%       100.00%
#nan      = 0             0             0             0
%nan      = 0.00%         0.00%         0.00%         0.00%
#inf      = 0             0             0             0
%inf      = 0.00%         0.00%         0.00%         0.00%
$

This is quite equivalent to the command

$ rubik -r 100 -e 'c0=cb.random_cube("6x9x32")' -e 'c0' -C \\
               -e 'c1=cb.random_cube("6x9x32")' -e 'c1' -C \\
               -e 'cb.rel_diff_cube(c0, c1)' -C \\
               -e 'cb.abs_diff_cube(c0, c1)' -C
shape     = 6x9x32        6x9x32        6x9x32        6x9x32
#elements = 1728          1728          1728          1728
%elements = 100.00%       100.00%       100.00%       100.00%
min       = 0.00048675947 1.4618569e-05 0.00038759335 0.00025051832
min_index = (1, 3, 13)    (1, 1, 13)    (4, 5, 19)    (4, 5, 19)
max       = 0.99947917    0.99867839    402.01849     0.98762667
max_index = (2, 0, 11)    (0, 5, 20)    (0, 3, 27)    (3, 3, 4)
sum       = 842.42566     860.05499     5523.7295     588.99091
ave       = 0.487515      0.497717      3.1966        0.340851
#zero     = 0             0             0             0
%zero     = 0.00%         0.00%         0.00%         0.00%
#nonzero  = 1728          1728          1728          1728
%nonzero  = 100.00%       100.00%       100.00%       100.00%
#nan      = 0             0             0             0
%nan      = 0.00%         0.00%         0.00%         0.00%
#inf      = 0             0             0             0
%inf      = 0.00%         0.00%         0.00%         0.00%
$

or, better, to the command

$ rubik -r 100 -e 'c0=cb.random_cube("6x9x32")' \\
               -e 'compare_stats(c0, title="LEFT")' \\
               -e 'c1=cb.random_cube("6x9x32")' \\
               -e 'compare_stats(c1, title="RIGHT")' \\
               -e 'cb.rel_diff_cube(c0, c1)' \\
               -e 'compare_stats(title="REL_DIFF")' \\
               -e 'cb.abs_diff_cube(c0, c1)' \\
               -e 'compare_stats(title="ABS_DIFF")'
name      = LEFT          RIGHT         REL_DIFF      ABS_DIFF
shape     = 6x9x32        6x9x32        6x9x32        6x9x32
#elements = 1728          1728          1728          1728
%elements = 100.00%       100.00%       100.00%       100.00%
min       = 0.00048675947 1.4618569e-05 0.00038759335 0.00025051832
min_index = (1, 3, 13)    (1, 1, 13)    (4, 5, 19)    (4, 5, 19)
max       = 0.99947917    0.99867839    402.01849     0.98762667
max_index = (2, 0, 11)    (0, 5, 20)    (0, 3, 27)    (3, 3, 4)
sum       = 842.42566     860.05499     5523.7295     588.99091
ave       = 0.487515      0.497717      3.1966        0.340851
#zero     = 0             0             0             0
%zero     = 0.00%         0.00%         0.00%         0.00%
#nonzero  = 1728          1728          1728          1728
%nonzero  = 100.00%       100.00%       100.00%       100.00%
#nan      = 0             0             0             0
%nan      = 0.00%         0.00%         0.00%         0.00%
#inf      = 0             0             0             0
%inf      = 0.00%         0.00%         0.00%         0.00%
$

<<<BREAK>>>
### 15. Out-of-core file statistics
Sometimes huge cubes are stored in files; they are too big to be processed
in memory, nevertheless it is possible to get statistics about them out-of-core.

* create two big cubes:

$ rubik -r 0 -e 'cb.write_random_cube("big0_{shape}.{format}", "100x100x100")'
$ rubik -r 1 -e 'cb.write_random_cube("big1_{shape}.{format}", "100x100x100")'
$

* show statistics out-of-core for the first cube:

$ rubik -e 'cb.print_stats_file("big0_{shape}.{format}", shape="100x100x100", block_size="1m")'
=== 26.214400%
shape     = 100x100x100
#elements = 262144
%elements = 26.21%
min       = 3.3105543e-06
min_index = (8, 43, 41)
max       = 0.99999899
max_index = (19, 82, 53)
sum       = 131122
ave       = 0.500189
#zero     = 0
%zero     = 0.00%
#nonzero  = 262144
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%

=== 52.428800%
shape     = 100x100x100
#elements = 524288
%elements = 52.43%
min       = 2.9504163e-06
min_index = (26, 39, 72)
max       = 0.99999899
max_index = (19, 82, 53)
sum       = 262123
ave       = 0.499959
#zero     = 0
%zero     = 0.00%
#nonzero  = 524288
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%

=== 78.643200%
shape     = 100x100x100
#elements = 786432
%elements = 78.64%
min       = 7.0712031e-07
min_index = (66, 15, 53)
max       = 0.99999899
max_index = (19, 82, 53)
sum       = 393464
ave       = 0.500315
#zero     = 0
%zero     = 0.00%
#nonzero  = 786432
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%

shape     = 100x100x100
#elements = 1000000
%elements = 100.00%
min       = 7.0712031e-07
min_index = (66, 15, 53)
max       = 0.9999997
max_index = (80, 18, 7)
sum       = 500391
ave       = 0.500391
#zero     = 0
%zero     = 0.00%
#nonzero  = 1000000
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
$

By default, the block_size is '1g'.

* show differences about the two cubes:

$ rubik -e 'cb.print_diff_files("big0_{shape}.{format}", "big1_{shape}.{format}", shape="100x100x100", block_size="2m")'
=== 52.428800%
name      = LEFT          RIGHT         REL_DIFF      ABS_DIFF
shape     = 100x100x100   100x100x100   100x100x100   100x100x100
#elements = 524288        524288        524288        524288
%elements = 52.43%        52.43%        52.43%        52.43%
min       = 2.9504163e-06 5.1598727e-06 3.5003384e-06 1.2069941e-06
min_index = (26, 39, 72)  (38, 14, 65)  (28, 67, 21)  (0, 12, 99)
max       = 0.99999899    0.99999821    283745.31     0.99896097
max_index = (19, 82, 53)  (48, 17, 89)  (8, 43, 41)   (10, 79, 78)
sum       = 262121        261956        3.30941e+06   174501
ave       = 0.499956      0.499641      6.3122        0.332834
#zero     = 0             0             0             0
%zero     = 0.00%         0.00%         0.00%         0.00%
#nonzero  = 524288        524288        524288        524288
%nonzero  = 100.00%       100.00%       100.00%       100.00%
#nan      = 0             0             0             0
%nan      = 0.00%         0.00%         0.00%         0.00%
#inf      = 0             0             0             0
%inf      = 0.00%         0.00%         0.00%         0.00%

name      = LEFT          RIGHT         REL_DIFF      ABS_DIFF
shape     = 100x100x100   100x100x100   100x100x100   100x100x100
#elements = 1000000       1000000       1000000       1000000
%elements = 100.00%       100.00%       100.00%       100.00%
min       = 7.0712031e-07 3.0077686e-07 1.5380414e-06 5.0663948e-07
min_index = (66, 15, 53)  (73, 4, 25)   (98, 7, 97)   (55, 51, 68)
max       = 0.9999997     0.99999958    879006.44     0.99896097
max_index = (80, 18, 7)   (70, 21, 31)  (66, 15, 53)  (10, 79, 78)
sum       = 500386        499944        7.38957e+06   332885
ave       = 0.500386      0.499944      7.38957       0.332885
#zero     = 0             0             0             0
%zero     = 0.00%         0.00%         0.00%         0.00%
#nonzero  = 1000000       1000000       1000000       1000000
%nonzero  = 100.00%       100.00%       100.00%       100.00%
#nan      = 0             0             0             0
%nan      = 0.00%         0.00%         0.00%         0.00%
#inf      = 0             0             0             0
%inf      = 0.00%         0.00%         0.00%         0.00%
$

<<<BREAK>>>
### 16. Check if two cubes are equal content within a given tolerance '1e-5':

$ rubik -i r_{shape}.{format} -s 8x10x20 -x i0=:,4,: \\
        -i rsub_y2_{shape}.{format} -s 8x20 \\
        -e 'cb.equals(i1, i0, 1e-5)' \\
        --print
True
$

<<<BREAK>>>
## 17. Print a random cube with integer values between -5 and +5:

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
## 18. Setting a single value on a cube:
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
## 19. Setting multiple values on a cube:
$ rubik -i r_{shape}.{format} -s 8x10x20 \\
        -e '_r[0, :, 3] = 4' \\
        -o o_{shape}.{format}
$

<<<BREAK>>>
## 20. Findinig indices where a given condition is True:
$ rubik -e 'cb.linear_cube("3x5")' \\
        -o l_{shape}.{format}
$ rubik -i l_{shape}.{format} \\
        -s 3x5 \\
        -e 'cb.where_indices(i0, i0 % 2 == 0)' \\
        --print
[[  0.   0.   0.]
 [  0.   2.   2.]
 [  0.   4.   4.]
 [  1.   1.   6.]
 [  1.   3.   8.]
 [  2.   0.  10.]
 [  2.   2.  12.]
 [  2.   4.  14.]]
$

<<<BREAK>>>
## 21. Create a big cube out of core:

Two functions are available to create big cubes out of core:
* write_linear_cube(file, shape, start=0.0, increment=1.0, buffer_size=None)
* write_random_cube(file, shape, min=0.0, max=1.0, buffer_size=None)
* write_const_cube(file, shape, value=0.0, buffer_size=None)


$ rubik 'cb.write_linear_cube("l.{shape}.raw", "3x4x5", buffer_size=2, start=-1, increment=0.5)'
$ rubik -i l.{shape}.raw -s 3x4x5 -v --print
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 60 'float32' elements (240 bytes) from 'raw' file 'l.3x4x5.raw'...
rubik: evaluating expression 'print_cube()'...
[[[ -1.   -0.5   0.    0.5   1. ]
  [  1.5   2.    2.5   3.    3.5]
  [  4.    4.5   5.    5.5   6. ]
  [  6.5   7.    7.5   8.    8.5]]

 [[  9.    9.5  10.   10.5  11. ]
  [ 11.5  12.   12.5  13.   13.5]
  [ 14.   14.5  15.   15.5  16. ]
  [ 16.5  17.   17.5  18.   18.5]]

 [[ 19.   19.5  20.   20.5  21. ]
  [ 21.5  22.   22.5  23.   23.5]
  [ 24.   24.5  25.   25.5  26. ]
  [ 26.5  27.   27.5  28.   28.5]]]
$ 

<<<BREAK>>>
## 22. Reading a portion of a file

$ rubik 'cb.linear_cube("3x4x5")' \\
        -o l.{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("3x4x5")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 60 'float32' elements (240 bytes) to 'raw' file 'l.3x4x5.raw'...
$ rubik -i l.3x{shape}.{format} \\
        -s 4x5 \\
        -Io 80b \\
        --print -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 20 'float32' elements (80 bytes) from 'raw' file 'l.3x4x5.raw'...
rubik: seeking 'l.3x4x5.raw'@80...
rubik: evaluating expression 'print_cube()'...
[[ 20.  21.  22.  23.  24.]
 [ 25.  26.  27.  28.  29.]
 [ 30.  31.  32.  33.  34.]
 [ 35.  36.  37.  38.  39.]]
$

<<<BREAK>>>
## 23. Overriding part of a file

$ rubik 'cb.linear_cube("3x4x5")' \\
        -o l.{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("3x4x5")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 60 'float32' elements (240 bytes) to 'raw' file 'l.3x4x5.raw'...
$ rubik 'cb.const_cube("4x5", value=1.5)' \\
        -o l.3x4x5.{format} \\
        -Oo 80b
$ rubik -i l.{shape}.{format} \\
        -s 3x4x5 \
        --print -v
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 60 'float32' elements (240 bytes) from 'raw' file 'l.3x4x5.raw'...
rubik: evaluating expression 'print_cube()'...
[[[  0.    1.    2.    3.    4. ]
  [  5.    6.    7.    8.    9. ]
  [ 10.   11.   12.   13.   14. ]
  [ 15.   16.   17.   18.   19. ]]

 [[  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]]

 [[ 40.   41.   42.   43.   44. ]
  [ 45.   46.   47.   48.   49. ]
  [ 50.   51.   52.   53.   54. ]
  [ 55.   56.   57.   58.   59. ]]]
$

This is equivalent to

$ rubik 'cb.linear_cube("3x4x5")' \\
        -o l2.{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("3x4x5")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 60 'float32' elements (240 bytes) to 'raw' file 'l2.3x4x5.raw'...
$ rubik -i l2.3x4x5.raw \\
        -s 3x4x5 \\
        'i0[1] = cb.const_cube("4x5", value=1.5)' \\
        -P
[[[  0.    1.    2.    3.    4. ]
  [  5.    6.    7.    8.    9. ]
  [ 10.   11.   12.   13.   14. ]
  [ 15.   16.   17.   18.   19. ]]

 [[  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]]

 [[ 40.   41.   42.   43.   44. ]
  [ 45.   46.   47.   48.   49. ]
  [ 50.   51.   52.   53.   54. ]
  [ 55.   56.   57.   58.   59. ]]]
$

Or also

$ rubik -i l2.3x4x5.raw \\
        -s 3x4x5 \\
        'i0[1] = 1.5' \\
        -P
[[[  0.    1.    2.    3.    4. ]
  [  5.    6.    7.    8.    9. ]
  [ 10.   11.   12.   13.   14. ]
  [ 15.   16.   17.   18.   19. ]]

 [[  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]
  [  1.5   1.5   1.5   1.5   1.5]]

 [[ 40.   41.   42.   43.   44. ]
  [ 45.   46.   47.   48.   49. ]
  [ 50.   51.   52.   53.   54. ]
  [ 55.   56.   57.   58.   59. ]]]
$

<<<BREAK>>>
## 24. Printing the histogram of a cube

$ rubik 'cb.random_cube("6x4x5")' --random-seed 100 -H
[0.00, 0.10)|****************************************                        |10
[0.10, 0.20)|********************************************************        |14
[0.20, 0.30)|****************************************************************|16
[0.30, 0.40)|****************************************************************|16
[0.40, 0.50)|********************                                            | 5
[0.50, 0.60)|********************************************                    |11
[0.60, 0.70)|********************************************************        |14
[0.70, 0.79)|********************************                                | 8
[0.79, 0.89)|****************************************************            |13
[0.89, 0.99]|****************************************************            |13
$ rubik 'cb.random_cube("6x4x5")' --random-seed 100 -H -Hb 5 -Hr 0.0 1.0
[0.0, 0.2)|**********************************************                    |23
[0.2, 0.4)|******************************************************************|33
[0.4, 0.6)|**************************************                            |19
[0.6, 0.8)|****************************************                          |20
[0.8, 1.0]|**************************************************                |25
$ rubik 'cb.random_cube("6x4x5")' --random-seed 100 -H -Hb 5 -Hr 0.0 1.0 -Hp
[0.0, 0.2)|*******************************************                   |19.17%
[0.2, 0.4)|**************************************************************|27.50%
[0.4, 0.6)|************************************                          |15.83%
[0.6, 0.8)|**************************************                        |16.67%
[0.8, 1.0]|***********************************************               |20.83%
$



"""
def help_cubes():
    help(cubes.api)

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
* the list of the input cubes '_i';
* the current result '_r' (which is generally a cube, but not necessarily).
* input/output functions

The 'cubes' module provides some numpy-based functions to operate with
cubes; see --help-cubes.

Input functions
===============
It is possible to read input files by using the following function:
* read_cube(
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
  )
  This is automatically set by '--input-filename/-i' option (and related
  input labeled options)

Output functions
================
It is possible to print/view the results using the following functions:
* write_cube(
        filename=None, 
        label=None, 
        cube=None,
        mode=None,
        offset=None,
        dtype=None,
        format=None,
        csv_separator=None,
        text_delimiter=None,
        text_newline=None,
        text_converter=None,
  )
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
* print_histogram(
        cube=None, 
        bins=None, 
        hrange=None, 
        decimals=None, 
        fmt=None,
  )
  This is automatically set by '--histogram/-H' option (and related
  histogram options)
* view(
        cube=None, 
        visualizer_type=None, 
        title=None,
  )
  This is automatically set by '--view/-V' option (and related
  visualizer options)

Expressions starting with '-'
=============================
If an expression starts with a '-' sign, rubik can try to parse it as an
option:

$ rubik '-cb.linear_cube("3x4")' --print
usage: rubik [-h] [--verbose] [--quiet] [--report] [--dry-run] [--version]
             [--logo] [--trace-errors] [--safe] [--optimized]
             [--optimized-min-size S] [--memory-limit L[units]] [--dtype D]
             [--accept-bigger-raw-files] [--clobber] [--no-clobber]
             [--random-seed RANDOM_SEED] [--warnings {RuntimeWarning,all}]
             [--source-file E [E ...]] [--expression E [E ...]]
             [--input-filename I [I ...]] [--shape [D0[:D1[...]]]]
             [--extract X] [--input-mode INPUT_MODES]
             [--input-offset INPUT_OFFSETS] [--input-dtype D]
             [--input-format INPUT_FORMATS] [--input-csv-separator S]
             [--input-text-delimiter D] [--output-filename O [O ...]]
             [--print-cube] [--print-stats] [--histogram] [--view]
             [--histogram-bins Hb] [--histogram-range Hr Hr]
             [--histogram-decimals Hd] [--histogram-length Hl]
             [--histogram-percentage] [--histogram-num] [--view-volume-slicer]
             [--view-volume-render] [--view-volume-contour] [--view-auto]
             [--view-attribute VA [VA ...]] [--view-attribute-file VF]
             [--view-list] [--split D] [--output-mode Om] [--output-offset Oo]
             [--output-dtype D] [--output-format Of]
             [--output-csv-separator S] [--output-text-delimiter D]
             [--output-text-newline N] [--output-text-converter C]
             [--help-dtypes] [--help-labeled-options] [--help-expression]
             [--help-extractor] [--help-user-defined-variables] [--help-numpy]
             [--help-cubes] [--help-filenames] [--help-split]
             [--help-environment-variables] [--help-creating-cubes]
             [--help-output] [--help-memory-usage] [--help-usage] [--demo]
             [expression [expression ...]]
rubik: error: unrecognized arguments: -cb.linear_cube("3x4")

In this case, there are some alternatives:

$ rubik -e'-cb.linear_cube("3x4")' --print
...
$ rubik -e='-cb.linear_cube("3x4")' --print
...
$ rubik --expression='-cb.linear_cube("3x4")' --print
...
$ rubik '0 - cb.linear_cube("3x4")' --print
...

It is also possible to use the '--' option to mark the end of options; 
nevertheless, in this case the '--print' option will not be recognized,
so the 'print_cube()' function must be called instead:

$ rubik -- '-cb.linear_cube("3x4")' 'print_cube()'
[[ -0.  -1.  -2.  -3.]
 [ -4.  -5.  -6.  -7.]
 [ -8.  -9. -10. -11.]]

or also

$ rubik 'print_cube(-cb.linear_cube("3x4"))'
[[ -0.  -1.  -2.  -3.]
 [ -4.  -5.  -6.  -7.]
 [ -8.  -9. -10. -11.]]

In the latter case, the '--' option is not necessary, since the expression
does not start with '-'.

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
rubik: evaluating expression "read_cube(label='i0')"...
rubik: reading 320 'float32' elements (1280 bytes) from 'raw' file 'a_8x4x10.raw'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.0.raw'...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.1.raw'...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.2.raw'...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 's_8x10.3.raw'...
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
  - the file operation mode
  - the offset
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
to set specific parameters on the output file, for instance the format.

For instance, '-o x=x_8x10.raw --output-dtype x=float64' applies the dtype
'float64' to the output file 'x_8x10.raw'.

Filename interpolation
======================
Filenames are interpolated; the following keywords are substituted:
* shape: the cube shape, for instance '3x2x4';
* rank: the cube shape rank, for instance '3' if the shape is '3x2x4';
* count: the number of elements, for instance '24' if the shape is '3x2x4';
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
These are the available output modes:
* print the result to a file (--print/-P, or function 'print_cube()')
* print statistics about the resulting cube (--stats/-S, or function
  'print_stats()')
* compare statistics about many resulting cubes (--compare-stats/-C, or
  function 'compare_stats()')
* show statistics about differences between two cubes (--diff/-D, or
  function 'diff()')
* print an histogram of the resulting cube to a file (--histogram/-H, or
  function 'print_histogram(...)')
* write the output cube to file (--output-filename/-o, or function 
  'write_cube(label=...)')
* visualization of the resulting cube (--view/-V, or function 'view()')
If the --dry-run/-d option is set, the previous mode are ignored, and no command
is executed.
It is possible to have a report of the rubik configuration, using the flag
--report/-R; it can be repeated to increase the report level.

Each output mode applies to the most recent result in the stack; so, for
instance, the following command will show only the linear cube:

$ rubik -e 'cb.linear_cube("5x3")' --print \\
        -e 'cb.const_cube("4x4", 2)'
[[  0.   1.   2.]
 [  3.   4.   5.]
 [  6.   7.   8.]
 [  9.  10.  11.]
 [ 12.  13.  14.]]

The following command

$ rubik -e 'cb.linear_cube("5x3")' --print \\
        -o 'l.raw' \\
        -e 'cb.const_cube("4x4", 2)' \\
        -o 'r.raw'

writes the linear cube to 'l.raw', the random cube to 'r.raw'.

It is possible to have many output modes for the same cube:

$ rubik -e 'cb.linear_cube("5x3")' --print --stats \\
        -e 'cb.const_cube("4x4", 2)' --print
[[  0.   1.   2.]
 [  3.   4.   5.]
 [  6.   7.   8.]
 [  9.  10.  11.]
 [ 12.  13.  14.]]
shape         = 5x3
#elements     = 15
min           = 0.0
max           = 14.0
sum           = 105.0
ave           = 7.0
#zero         = 1 [6.67%]
#nonzero      = 14 [93.33%]
#nan          = 0 [0.00%]
#inf          = 0 [0.00%]

[[ 2.  2.  2.  2.]
 [ 2.  2.  2.  2.]
 [ 2.  2.  2.  2.]
 [ 2.  2.  2.  2.]]

It is possible to use expressions to call specific output modes:

$ rubik -e 'cb.linear_cube("5x3")' 'print_stats()'
shape         = 5x3
#elements     = 15
min           = 0.0
max           = 14.0
sum           = 105.0
ave           = 7.0
#zero         = 1 [6.67%]
#nonzero      = 14 [93.33%]
#nan          = 0 [0.00%]
#inf          = 0 [0.00%]


Visualization can be performed on multiple cubes, only if they all have the same
shape.

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
        #example.dump(test=True, interactive=False)
        #raw_input("...")
        example.show(test=True, interactive=False)

def help_demo():
    with chtempdir():
        example = Example(_DEMO_TEXT)
        example.show(test=True, interactive=True)
