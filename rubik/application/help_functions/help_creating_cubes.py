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
              'HelpCreatingCubes',
              'help_creating_cubes',
          ]

from .functor_help_example import HelpExample

def help_creating_cubes(test=None, interactive=None, writer=None):
    HelpCreatingCubes(test=test, interactive=interactive, writer=writer)()

class HelpCreatingCubes(HelpExample):
    TEXT = """\
# Creating cubes from scratch

It is possible to create cubes from scratch, using an expression.  For instance:

$ rubik -e 'np.linspace(0, 79, 80).reshape((8, 10))' -o lc_{shape}.{format} -v
rubik: evaluating expression 'np.linspace(0, 79, 80).reshape((8, 10))'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 'lc_8x10.raw'...
$

will create a cube with values from 0.0 to 79.0 with increment 1.0.

<<<BREAK>>>

The cubes (or cb) module has some convenience functions to easily
create cubes:

$ rubik -e 'cb.linear_cube("8x10")' -o lc_{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("8x10")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 'lc_8x10.raw'...
$

creates the same cube;

$ rubik -e 'cb.random_cube("8x10")' -o rc_{shape}.{format} -v
rubik: evaluating expression 'cb.random_cube("8x10")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 'rc_8x10.raw'...
$

creates a random cube; and

$ rubik -e 'cb.const_cube("8x10", 8.0)' -o cc_{shape}.{format} -v
rubik: evaluating expression 'cb.const_cube("8x10", 8.0)'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 80 'float32' elements (320 bytes) to 'raw' file 'cc_8x10.raw'...
$

creates a const cube with all values 8.0.

$ rubik -e 'cb.const_blocks_cube("8x10x4", start=0.0, increment=1.0, const_dims=[1, 2])' \\
        -o cc_{shape}.{format} -v
rubik: evaluating expression 'cb.const_blocks_cube("8x10x4", start=0.0, increment=1.0, const_dims=[1, 2])'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 320 'float32' elements (1280 bytes) to 'raw' file 'cc_8x10x4.raw'...
$

creates a cube _r for which each subcube _r[x, :, :] is const, with value 'x'.

<<<BREAK>>>

In general, if the cube is N-dimensional, every subcube obtained by fixing
all the coordinates except those listed in const_dims (d_a, d_b, d_c, ...) has
const values. Moreover, the first subcube corresponding to (0, 0, ..., 0) has
value 'start', the second, corresponding to (0, 0, ..., 1) has value 'start + 
increment', and so on.

See --help-cubes to see the content of the cubes module.
"""
