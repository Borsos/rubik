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
           'linear_cube', 'random_cube', 'const_cube', 'const_blocks_cube',
           'write_linear_cube', 'write_random_cube', 'write_const_cube',
           'fromfile_generic', 'fromfile_raw', 'fromfile_text', 'fromfile_csv',
           'not_equals_cube', 'not_equals_num', 'not_equals',
           'equals_cube', 'equals_num', 'equals',
           'reldiff_cube', 'threshold_cube',
           'absdiff_cube', 'abs_threshold_cube',
           'where_indices',
           'nonzero_cube',
           'join',
          ]

from .creation import linear_cube, random_cube, const_cube, const_blocks_cube, \
                      join

from .io import fromfile_generic, fromfile_raw, fromfile_text, fromfile_csv, \
                write_linear_cube, write_random_cube, write_const_cube

from .comparison import not_equals_cube, not_equals_num, not_equals, \
                        equals_cube, equals_num, equals, \
                        reldiff_cube, threshold_cube, \
                        absdiff_cube, abs_threshold_cube, \
                        where_indices, \
                        nonzero_cube
