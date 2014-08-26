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
           'StatsInfo',
           'stats_cube',
           'print_stats',
          ]

import sys
import numpy as np

from ..errors import RubikError
from .internals import output_mode_callback

class StatsInfo(object):
    """StatsInfo(...)
       collect statistics about a cube:
        o cube_shape
        o cube_count
        o cube_sum
        o cube_ave
        o cube_min
        o cube_max
        o cube_count_zero
        o cube_count_nonzero
        o cube_count_nan
        o cube_count_inf
    """
    def __init__(self,
            cube_shape=None,
            cube_count=0,
            cube_sum=0,
            cube_ave=None, 
            cube_min=None, 
            cube_max=None, 
            cube_count_zero=0,
            cube_count_nonzero=0,
            cube_count_nan=0,
            cube_count_inf=0):
        self.cube_shape = cube_shape
        self.cube_sum = cube_sum
        self.cube_count = cube_count
        self.cube_count_zero = cube_count_zero
        self.cube_count_nonzero = cube_count_nonzero
        self.cube_count_nan = cube_count_nan
        self.cube_count_inf = cube_count_inf
        self.cube_min = cube_min
        self.cube_max = cube_max

    @property
    def cube_fraction_zero(self):
        if self.cube_count:
            return self.cube_count_zero / float(self.cube_count)

    @property
    def cube_fraction_nonzero(self):
        if self.cube_count:
            return self.cube_count_nonzero / float(self.cube_count)

    @property
    def cube_fraction_nan(self):
        if self.cube_count:
            return self.cube_count_nan / float(self.cube_count)

    @property
    def cube_fraction_inf(self):
        if self.cube_count:
            return self.cube_count_inf / float(self.cube_count)

    @property
    def cube_ave(self):
        if self.cube_count:
            return self.cube_sum / float(self.cube_count)

    @classmethod
    def get_op(cls, op, v0, v1):
        if v0 is None:
            return v1
        elif v1 is None:
            return v0
        else:
            return op(v0, v1)

    @classmethod
    def get_min(cls, v0, v1):
        return cls.get_op(min, v0, v1)

    @classmethod
    def get_max(cls, v0, v1):
        return cls.get_op(max, v0, v1)

    def __iadd__(self, stats_info):
        if not isinstance(stats_info, StatsInfo):
            raise RubikError("cannot sum {} with {}".format(type(self).__name__, type(stats_info).__name__))
        if self.cube_shape is None:
            self.cube_shape = stats_info.cube_shape
        elif stats_info.cube_shape is not None and stats_info.cube_shape != self.cube_shape:
            raise RubikError("cannot sum {} objects with mismatching shapes: {} {}".format(type(self).__name__, self.cube_shape, stats_info.cube_shape))
        self.cube_sum += stats_info.cube_sum
        self.cube_count += stats_info.cube_count
        self.cube_count_zero += stats_info.cube_count_zero
        self.cube_count_nonzero += stats_info.cube_count_nonzero
        self.cube_count_nan += stats_info.cube_count_nan
        self.cube_count_inf += stats_info.cube_count_inf
        print self.cube_min, self.cube_max
        self.cube_min = self.get_min(self.cube_min, stats_info.cube_min)
        self.cube_max = self.get_max(self.cube_min, stats_info.cube_max)
        return self

    def __add__(self, stats_info):
        result = self.__class__()
        result += stats_info
        return result

def stats_cube(cube):
    """stats_cube(cube) -> StatsInfo
       creates a StatsInfo object from a cube
    """
    if not isinstance(cube, np.ndarray):
        raise RubikError("cannot make an histogram from result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
    cube_sum = cube.sum()
    cube_ave = None
    if cube.shape != 0:
        cube_count = 1
        for d in cube.shape:
            cube_count *= d
    else:
        cube_count = 0
    if cube_count:
        cube_ave = cube_sum / float(cube_count)
    else:
        cube_ave = None
    cube_count_nonzero = np.count_nonzero(cube)
    cube_count_zero = cube_count - cube_count_nonzero
    cube_count_nan = np.count_nonzero(np.isnan(cube))
    cube_count_inf = np.count_nonzero(np.isinf(cube))
    stats_info = StatsInfo(
        cube_shape=cube.shape,
        cube_sum=cube_sum,
        cube_count=cube_count,
        cube_min=cube.min(),
        cube_max=cube.max(),
        cube_count_zero=cube_count_zero,
        cube_count_nonzero=cube_count_nonzero,
        cube_count_nan=cube_count_nan,
        cube_count_inf=cube_count_inf,
    )
    return stats_info

def print_stats(stats_info, stream=None, print_function=None):
    """print_stats(stats_info, stream=None, print_function=None)
       print a StatsInfo object
    """

    output_mode_callback()
    if stream is None:
        stream = sys.stdout
    if print_function is None:
        print_function = lambda x: stream.write(x + '\n')
    
    s_shape = "<undefined>"
    if stats_info.cube_shape is not None:
        s_shape = 'x'.join(str(e) for e in stats_info.cube_shape)

    print_function("""\
shape         = {shape}
#elements     = {count}
min           = {min}
max           = {max}
sum           = {sum}
ave           = {ave}
#zero         = {count_zero} [{fraction_zero:.2%}]
#nonzero      = {count_nonzero} [{fraction_nonzero:.2%}]
#nan          = {count_nan} [{fraction_nan:.2%}]
#inf          = {count_inf} [{fraction_inf:.2%}]
""".format(
            shape=s_shape,
            min=stats_info.cube_min,
            max=stats_info.cube_max,
            sum=stats_info.cube_sum,
            ave=stats_info.cube_ave,
            count=stats_info.cube_count,
            count_zero=stats_info.cube_count_zero,
            fraction_zero=stats_info.cube_fraction_zero,
            count_nonzero=stats_info.cube_count_nonzero,
            fraction_nonzero=stats_info.cube_fraction_nonzero,
            count_nan=stats_info.cube_count_nan,
            fraction_nan=stats_info.cube_fraction_nan,
            count_inf=stats_info.cube_count_inf,
            fraction_inf=stats_info.cube_fraction_inf,
        )
    )


