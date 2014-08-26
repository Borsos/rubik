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
           'CubeInfo',
           'StatsInfo',
           'stats_info',
           'cube_info',
           'print_stats',
          ]

import sys
import numpy as np

from ..errors import RubikError
from .internals import output_mode_callback

class Info(object):
    @classmethod
    def get_print_function(cls, print_function=None):
        if print_function is None:
            print_function = lambda x: sys.stdout.write(x + '\n')
        return print_function

    def print_report(self, print_function=None):
        print_function = self.get_print_function(print_function)
        print_function(self.report())
        
    def report(self):
        pass

class CubeInfo(Info):
    """CubeInfo(...)
       information about a cube:
        o shape
    """
    def __init__(self,
            cube_shape=None,
    ):
        self.cube_shape = cube_shape
    
    @classmethod
    def cube_info(cls, cube):
        """cube_info(cube) -> CubeInfo
           creates a CubeInfo object from a cube
        """
        if not isinstance(cube, np.ndarray):
            raise RubikError("cannot make an histogram from result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
        cube_info = CubeInfo(
            cube_shape=cube.shape,
        )
        return cube_info

    def report(self):
        """report(self) -> CubeInfo report
        """
        s_shape = "<undefined>"
        if self.cube_shape is not None:
            s_shape = 'x'.join(str(e) for e in self.cube_shape)
        return """\
shape         = {shape}""".format(
            shape=s_shape,
        )

cube_info = CubeInfo.cube_info

class StatsInfo(Info):
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
            cube_count=0,
            cube_sum=0,
            cube_ave=None, 
            cube_min=None, 
            cube_max=None, 
            cube_count_zero=0,
            cube_count_nonzero=0,
            cube_count_nan=0,
            cube_count_inf=0):
        self.cube_sum = cube_sum
        self.cube_count = cube_count
        self.cube_count_zero = cube_count_zero
        self.cube_count_nonzero = cube_count_nonzero
        self.cube_count_nan = cube_count_nan
        self.cube_count_inf = cube_count_inf
        self.cube_min = cube_min
        self.cube_max = cube_max

    @classmethod
    def stats_info(cls, cube):
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

    def report(self):
        """report(self) -> StatsInfo report
        """

        return """\
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
            min=self.cube_min,
            max=self.cube_max,
            sum=self.cube_sum,
            ave=self.cube_ave,
            count=self.cube_count,
            count_zero=self.cube_count_zero,
            fraction_zero=self.cube_fraction_zero,
            count_nonzero=self.cube_count_nonzero,
            fraction_nonzero=self.cube_fraction_nonzero,
            count_nan=self.cube_count_nan,
            fraction_nan=self.cube_fraction_nan,
            count_inf=self.cube_count_inf,
            fraction_inf=self.cube_fraction_inf,
        )

stats_info = StatsInfo.stats_info

def print_stats(cube, stream=None, print_function=None):
    output_mode_callback()
    cube_info = CubeInfo.cube_info(cube)
    cube_info.print_report()
    stats_info = StatsInfo.stats_info(cube)
    stats_info.print_report()
    

