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
              'HelpMemoryUsage',
              'help_memory_usage',
          ]

from .functor_help_example import HelpExample

def help_memory_usage(test=None, interactive=None, writer=None):
    HelpMemoryUsage(test=test, interactive=interactive, writer=writer)()

class HelpMemoryUsage(HelpExample):
    TEXT = """\
# Memory usage

A complete control of the memory usage is not possible, due to the possibility
to execute generic expressions involving numpy arrays. Nevertheless rubik can
check the amount of memory necessary to read input files and store the result.
You can provide a limit for this amout of memory using the '--memory-limit/m'
option.

For instance, with the option '--memory-limit 16gb', you will not allowed to
read more than 16 gb of data. The default memory limit is '0', which means no
limit.

# Optimized read vs direct read

When loading input files, two algorithms are available:
* optimized read
* direct read
The optimized read is memory efficient: if an extractor is used, it is applied
directly during the read, so only the exact amount of memory to store the
subcube is used. On the opposite, the direct read reads the full cube, and
then applies the extractor in memory.

The direct algorithm is used when the extractor is missing, or when the
extracted subcube has the same size as the input cube. Moreover, the direct
algorithm is used if the size of the input cube is lower than a limit that
can be set through the '--read-threshold-size' option. For instance, if
'--read-threshold-size 1gb', the direct algorithm is always used if the input
file is less than 1gb. By default, the read_threshold_size is 100mb.

The 'read_threshold_size' parameter can be used to switch from one algorithm to
the other; when less than 'read_threshold_size' bytes have to be read, the
direct read is used, otherwise the optimized read algorithm is performed.

The optimized read&extract algorithm is iterative: when it is applied, only the
necessary indices of the slowest dimension are read. For instance:

* shape: "10x10x10"
* extractor: "5:,::2,10"

The slowest dimension extractor is '5:', so only these five indices are read;
so, the algorithm is then applied to 5 "10x10" subcubes. The optimized algorithm
is iterated until the subcube size is less than read_threshold_size (or the
related extractor extracts all the subcube, i.e. it is ':' for all the
dimensions): in this case, the full subcube is read, and then the related
extractor is applied.

"""
