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
              'help_split',
              'HelpSplit',
          ]

from .functor_help_example import HelpExample

def help_split(test=None, interactive=None, writer=None):
    HelpSplit(test=test, interactive=interactive, writer=writer)()

class HelpSplit(HelpExample):
    TEXT = """\
# Splitting dimensions

Suppose you have a _8x4x10_ cube, and you want to write _4_ _8x10_ cubes, one
for each index in the second dimension. The command is:

$ rubik -e 'cb.linear_cube("8x4x10")' \\
        -o a_{shape}.{format} -v
rubik: evaluating expression 'cb.linear_cube("8x4x10")'...
rubik: evaluating expression "write_cube(label='o0')"...
rubik: writing 320 'float32' elements (1280 bytes) to 'raw' file 'a_8x4x10.raw'...
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
 
"""
