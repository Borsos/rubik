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
              'HelpUsage',
              'help_usage',
              'help_demo',
          ]

from .functor_help_example import HelpExample

def help_usage(test=None, interactive=False, writer=None):
    HelpUsage(test=test, interactive=interactive, writer=writer)()

def help_demo(test=None, interactive=True, writer=None):
    HelpUsage(test=test, interactive=interactive, writer=writer)()

class HelpUsage(HelpExample):
    TEXT = """\
# Examples/recipes

## 1. Create a random cube with a given shape:

$ rubik -r 100 -e 'cb.random_cube("8x10x20")' -o r_{shape}.{format}
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
        -e 'cb.join(_i)' \
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
sum       = 79.3741
ave       = 0.496088
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
sum       = 842.425       860.055       1801.83
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
sum       = 842.425       860.055       5523.73       588.99
ave       = 0.487515      0.497717      3.19661       0.340851
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
sum       = 842.425       860.055       5523.73       588.99
ave       = 0.487515      0.497717      3.19661       0.340851
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
sum       = 842.425       860.055       5523.73       588.99
ave       = 0.487515      0.497717      3.19661       0.340851
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

$ rubik -e 'cb.print_stats_file("big0_{shape}.{format}", shape="100x100x100", buffer_size="1m")'
=== 26.214400%
shape     = 100x100x100
#elements = 262144
%elements = 26.21%
min       = 3.3105543e-06
min_index = (8, 43, 41)
max       = 0.99999899
max_index = (19, 82, 53)
sum       = 131122
ave       = 0.500193
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
sum       = 262122
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
sum       = 393462
ave       = 0.500313
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
sum       = 500388
ave       = 0.500388
#zero     = 0
%zero     = 0.00%
#nonzero  = 1000000
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
$

By default, the buffer_size is '1g'.

* show differences about the two cubes:

$ rubik -e 'cb.print_diff_files("big0_{shape}.{format}", "big1_{shape}.{format}", shape="100x100x100", buffer_size="2m")'
=== 52.428800%
name      = LEFT          RIGHT         REL_DIFF      ABS_DIFF
shape     = 100x100x100   100x100x100   100x100x100   100x100x100
#elements = 524288        524288        524288        524288
%elements = 52.43%        52.43%        52.43%        52.43%
min       = 2.9504163e-06 5.1598727e-06 3.5003384e-06 1.2069941e-06
min_index = (26, 39, 72)  (38, 14, 65)  (28, 67, 21)  (0, 12, 99)
max       = 0.99999899    0.99999821    283745.31     0.99896097
max_index = (19, 82, 53)  (48, 17, 89)  (8, 43, 41)   (10, 79, 78)
sum       = 262122        261960        3.3098e+06    174506
ave       = 0.499959      0.499648      6.31295       0.332843
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
sum       = 500388        499948        7.3905e+06    332895
ave       = 0.500388      0.499948      7.3905        0.332895
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


$ rubik -e 'cb.write_linear_cube("l.{shape}.raw", "3x4x5", buffer_size=2, start=-1, increment=0.5)'
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

$ rubik -e 'cb.linear_cube("3x4x5")' \\
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

$ rubik -e 'cb.linear_cube("3x4x5")' \\
        -o l.{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("3x4x5")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 60 'float32' elements (240 bytes) to 'raw' file 'l.3x4x5.raw'...
$ rubik -e 'cb.const_cube("4x5", value=1.5)' \\
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

$ rubik -e 'cb.linear_cube("3x4x5")' \\
        -o l2.{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("3x4x5")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 60 'float32' elements (240 bytes) to 'raw' file 'l2.3x4x5.raw'...
$ rubik -i l2.3x4x5.raw \\
        -s 3x4x5 \\
        -e 'i0[1] = cb.const_cube("4x5", value=1.5)' \\
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
        -e 'i0[1] = 1.5' \\
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

$ rubik -e 'cb.random_cube("6x4x5")' --random-seed 100 -H
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
$ rubik -e 'cb.random_cube("6x4x5")' --random-seed 100 -H -Hb 5 -Hr 0.0 1.0
[0.0, 0.2)|**********************************************                    |23
[0.2, 0.4)|******************************************************************|33
[0.4, 0.6)|**************************************                            |19
[0.6, 0.8)|****************************************                          |20
[0.8, 1.0]|**************************************************                |25
$ rubik -e 'cb.random_cube("6x4x5")' --random-seed 100 -H -Hb 5 -Hr 0.0 1.0 -Hp
[0.0, 0.2)|*******************************************                   |19.17%
[0.2, 0.4)|**************************************************************|27.50%
[0.4, 0.6)|************************************                          |15.83%
[0.6, 0.8)|**************************************                        |16.67%
[0.8, 1.0]|***********************************************               |20.83%
$

"""

