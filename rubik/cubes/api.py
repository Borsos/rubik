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
           'linear_cube',
           'random_cube',
           'const_cube',
           'const_blocks_cube',
           'write_linear_cube',
           'write_random_cube',
           'write_const_cube',
           'read_cube',
           'read_cube_raw',
           'read_cube_text',
           'read_cube_csv',
           'write_cube',
           'write_cube_raw',
           'write_cube_text',
           'write_cube_csv',
           'not_equals_cube',
           'not_equals_num',
           'not_equals',
           'equals_cube',
           'equals_num',
           'equals',
           'rel_diff_cube',
           'threshold_cube',
           'abs_diff_cube',
           'abs_threshold_cube',
           'where_indices',
           'zero_cube',
           'nonzero_cube',
           'split',
           'join',
           'StatsInfo',
           'stats_info',
           'DiffInfo',
           'diff_info',
           'print_stats',
           'print_diff',
           'stats_file',
           'print_stats_file',
           'diff_files',
           'print_diff_files',
           'precise_sum',
           'precise_mean',
           'set_random_seed',
           'get_dtype',
           'get_default_dtype',
           'get_dtype_name',
           'as_dtype',
           'best_precise_dtype',
           'interpolate_filename',
           'histogram',
           'print_histogram',
          ]

from .operation import \
    split, \
    join

from .creation import \
    linear_cube, \
    random_cube, \
    const_cube, \
    const_blocks_cube

from .input_output import \
    read_cube, \
    read_cube_raw, \
    read_cube_text, \
    read_cube_csv, \
    write_cube, \
    write_cube_raw, \
    write_cube_text, \
    write_cube_csv, \
    write_linear_cube, \
    write_random_cube, \
    write_const_cube

from .comparison import \
    not_equals_cube, \
    not_equals_num, \
    not_equals, \
    equals_cube, \
    equals_num, \
    equals, \
    rel_diff_cube, \
    threshold_cube, \
    abs_diff_cube, \
    abs_threshold_cube, \
    where_indices, \
    zero_cube, \
    nonzero_cube

from .stats import \
    StatsInfo, \
    stats_info, \
    DiffInfo, \
    diff_info, \
    print_stats, \
    print_diff, \
    stats_file, \
    print_stats_file, \
    diff_files, \
    print_diff_files

from .dtypes import \
    best_precise_dtype, \
    get_dtype, \
    get_default_dtype, \
    get_dtype_name, \
    as_dtype

from .internals import \
    set_random_seed

from .utilities import \
    precise_sum, \
    precise_mean, \
    interpolate_filename

from .histogram import \
    histogram, \
    print_histogram
