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
              'HelpOutput',
              'help_output',
          ]

from .functor_help_example import HelpExample

def help_output(test=None, interactive=None, writer=None):
    HelpOutput(test=test, interactive=interactive, writer=writer)()

class HelpOutput(HelpExample):
    TEXT = """\
# Output modes

These are the available output modes:
* print the result to a file (--print/-P, or function 'print_cube()')
* print statistics about the resulting cube (--stats/-S, or function
  'print_stats()')
* compare statistics about many resulting cubes (--compare-stats/-C, or
  function 'compare_stats()'); this is similar to --stats/-S, but all
  the stats are shown side by side
* show statistics about differences between two cubes (--diff/-D, or
  function 'diff()')
* print an histogram of the resulting cube to a file (--histogram/-H, or
  function 'print_histogram(...)')
* write the output cube to file (--output-filename/-o, or function 
  'write_cube(label=...)')
* visualization of the resulting cube (--view/-V, or function 'view()')

If the --dry-run/-d option is set, the previous mode are ignored, and no command
is executed.

<<<BREAK>>>

It is possible to have a report of the rubik configuration, using the flag
--report/-R; it can be repeated to increase the report level.

<<<BREAK>>>

Each output mode applies to the most recent result in the stack; so, for
instance, the following command will show only the linear cube:

$ rubik -e 'cb.linear_cube("5x3")' --print \\
        -e 'cb.const_cube("4x4", 2)'
[[  0.   1.   2.]
 [  3.   4.   5.]
 [  6.   7.   8.]
 [  9.  10.  11.]
 [ 12.  13.  14.]]
rubik: WARNING: pointless expression 'cb.const_cube("4x4", 2)'
$

The second expression is pointless, as shown by the warning message.

<<<BREAK>>>

The following command

$ rubik -e 'cb.linear_cube("5x3")' --print \\
        -o 'l.raw' \\
        -e 'cb.const_cube("4x4", 2)' \\
        -o 'r.raw'
[[  0.   1.   2.]
 [  3.   4.   5.]
 [  6.   7.   8.]
 [  9.  10.  11.]
 [ 12.  13.  14.]]
$

writes the linear cube to 'l.raw', the random cube to 'r.raw'.

It is possible to have many output modes for the same cube:

$ rubik -e 'cb.linear_cube("5x3")' --print --stats \\
        -e 'cb.const_cube("4x4", 2)' --print
[[  0.   1.   2.]
 [  3.   4.   5.]
 [  6.   7.   8.]
 [  9.  10.  11.]
 [ 12.  13.  14.]]
shape     = 5x3
#elements = 15
%elements = 100.00%
min       = 0.0
min_index = (0, 0)
max       = 14.0
max_index = (4, 2)
sum       = 105
ave       = 7
#zero     = 1
%zero     = 6.67%
#nonzero  = 14
%nonzero  = 93.33%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
[[ 2.  2.  2.  2.]
 [ 2.  2.  2.  2.]
 [ 2.  2.  2.  2.]
 [ 2.  2.  2.  2.]]
$

It is possible to use expressions to call specific output modes:

$ rubik -e 'cb.linear_cube("5x3")' 'print_stats()'
shape     = 5x3
#elements = 15
%elements = 100.00%
min       = 0.0
min_index = (0, 0)
max       = 14.0
max_index = (4, 2)
sum       = 105
ave       = 7
#zero     = 1
%zero     = 6.67%
#nonzero  = 14
%nonzero  = 93.33%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
$

Visualization can be performed on multiple cubes, only if they all have the same
shape.

"""
