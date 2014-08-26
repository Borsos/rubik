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
           'cube_info',
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
          ]

import sys
import numpy as np

from ..errors import RubikError
from ..shape import Shape
from .internals import output_mode_callback
from .comparison import reldiff_cube, absdiff_cube
from .input_output import fromfile_raw
from .out_of_core import iterate_over_blocks

class Info(object):
    @classmethod
    def get_print_function(cls, print_function=None):
        if print_function is None:
            print_function = lambda x: sys.stdout.write(x + '\n')
        return print_function

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
        self.cube_shape = Shape(cube_shape)
    
    @classmethod
    def cube_info(cls, cube):
        """cube_info(cube) -> CubeInfo
           creates a CubeInfo object from a cube
        """
        if not isinstance(cube, np.ndarray):
            raise RubikError("cannot stat object of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
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
            raise RubikError("cannot stat object of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
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
        else:
            return 0.0

    @property
    def cube_fraction_nonzero(self):
        if self.cube_count:
            return self.cube_count_nonzero / float(self.cube_count)
        else:
            return 0.0

    @property
    def cube_fraction_nan(self):
        if self.cube_count:
            return self.cube_count_nan / float(self.cube_count)
        else:
            return 0.0

    @property
    def cube_fraction_inf(self):
        if self.cube_count:
            return self.cube_count_inf / float(self.cube_count)
        else:
            return 0.0

    @property
    def cube_ave(self):
        if self.cube_count:
            return self.cube_sum / float(self.cube_count)
        else:
            return 0.0

    def __iadd__(self, stats_info):
        if not isinstance(stats_info, StatsInfo):
            raise RubikError("cannot sum {} with {}".format(type(self).__name__, type(stats_info).__name__))
        self.cube_sum += stats_info.cube_sum
        self.cube_count += stats_info.cube_count
        self.cube_count_zero += stats_info.cube_count_zero
        self.cube_count_nonzero += stats_info.cube_count_nonzero
        self.cube_count_nan += stats_info.cube_count_nan
        self.cube_count_inf += stats_info.cube_count_inf
        self.cube_min = self.get_min(self.cube_min, stats_info.cube_min)
        self.cube_max = self.get_max(self.cube_max, stats_info.cube_max)
        return self

    def __add__(self, stats_info):
        result = self.__class__()
        result += self
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

class DiffInfo(Info):
    """DiffInfo(...)
       collect statistics about differences between two cubes:
        o stats_info_0
        o stats_info_1
        o min_rel_err
        o max_rel_err
        o min_abs_err
        o max_abs_err"""
    def __init__(self,
        stats_info_0=None,
        stats_info_1=None,
        min_rel_err=None,
        max_rel_err=None,
        min_abs_err=None,
        max_abs_err=None,
    ):
        if stats_info_0 is None:
            stats_info_0 = StatsInfo()
        if stats_info_1 is None:
            stats_info_1 = StatsInfo()
        self.stats_info_0 = stats_info_0
        self.stats_info_1 = stats_info_1
        self.min_rel_err = min_rel_err
        self.max_rel_err = max_rel_err
        self.min_abs_err = min_abs_err
        self.max_abs_err = max_abs_err

    def __iadd__(self, diff_info):
        self.stats_info_0 += diff_info.stats_info_0
        self.stats_info_1 += diff_info.stats_info_1
        self.min_rel_err = self.get_min(self.min_rel_err, diff_info.min_rel_err)
        self.max_rel_err = self.get_max(self.max_rel_err, diff_info.max_rel_err)
        self.min_abs_err = self.get_min(self.min_abs_err, diff_info.min_abs_err)
        self.max_abs_err = self.get_max(self.max_abs_err, diff_info.max_abs_err)
        return self

    def __add__(self, diff_info):
        result = self.__class__()
        result += self
        result += diff_info
        return result

    @classmethod
    def diff_info(cls, cube_0, cube_1, in_threshold=None, out_threshold=None):
        rcube = reldiff_cube(cube_0, cube_1, in_threshold=in_threshold, out_threshold=out_threshold)
        min_rel_err = rcube.min()
        max_rel_err = rcube.max()
        acube = absdiff_cube(cube_0, cube_1, in_threshold=in_threshold, out_threshold=out_threshold)
        min_abs_err = acube.min()
        max_abs_err = acube.max()
        return cls(
            stats_info_0=StatsInfo.stats_info(cube_0),
            stats_info_1=StatsInfo.stats_info(cube_1),
            min_rel_err=min_rel_err,
            max_rel_err=max_rel_err,
            min_abs_err=min_abs_err,
            max_abs_err=max_abs_err,
        )

    def report(self):
        return """\
=== cube[0]:
{stats_info_0}
=== cube[1]:
{stats_info_1}
=== diff:
min_rel_err   = {min_rel_err}
max_rel_err   = {max_rel_err}
min_abs_err   = {min_abs_err}
max_abs_err   = {max_abs_err}
""".format(
            stats_info_0=self.stats_info_0.report(),
            stats_info_1=self.stats_info_1.report(),
            min_rel_err=self.min_rel_err,
            max_rel_err=self.max_rel_err,
            min_abs_err=self.min_abs_err,
            max_abs_err=self.max_abs_err,
        )

diff_info = DiffInfo.diff_info

def print_stats(cube, print_function=None):
    """print_stats(cube, print_function=None)
    print statistics about cube
    """
    output_mode_callback()
    cube_info = CubeInfo.cube_info(cube)
    cube_info.print_report(print_function=print_function)
    stats_info = StatsInfo.stats_info(cube)
    stats_info.print_report(print_function=print_function)
    
def print_diff(cube_0, cube_1, print_function=None):
    """print_diff(cube_0, cube_1, print_function=None)
    print statistics about cube_0, cube_1, and their diff
    """
    output_mode_callback()
    cube_info_0 = CubeInfo.cube_info(cube_0)
    cube_info_1 = CubeInfo.cube_info(cube_1)
    if cube_info_0.cube_shape != cube_info_1.cube_shape:
        raise RubikError("cannot diff cubes with different shape {} and {}".format(
            cube_info_0.cube_shape,
            cube_info_1.cube_shape,
        ))
    cube_info_0.print_report(print_function=print_function, in_threshold=None, out_threshold=None)
    diff_info = DiffInfo.diff_info(cube_0, cube_1, in_threshold=in_threshold, out_threshold=out_threshold)
    diff_info.print_report(print_function=print_function)

def stats_file(filename, shape, dtype=None, ooc=True, block_size=None):
    """stats_file(filename, shape, dtype=None, ooc=True, block_size=None) -> StatsInfo object
    returns a StatsInfo about the content of 'filename', which is a cube with 'shape'.
    If 'ooc' (out-of-core) is True, process 'block_size' elements at a time.
    """
    if ooc:
        stats_info = stats_info_ooc(filename, shape=shape, dtype=dtype, block_size=block_size)
    else:
        cube = fromfile_raw(filename, shape=shape, dtype=dtype)
        stats_info = StatsInfo.stats_info(cube)
    return stats_info

def print_stats_file(filename, shape, dtype=None, ooc=True, block_size=None, print_function=None):
    """print_stats_file(filename, shape, dtype=None, ooc=True, block_size=None, print_function=None)
    prints the StatsInfo about the content of 'filename', which is a cube with 'shape'.
    If 'ooc' (out-of-core) is True, process 'block_size' elements at a time.
    """
    output_mode_callback()
    cube_info = CubeInfo(cube_shape=shape)
    stats_info = stats_file(filename, shape=shape, dtype=dtype, ooc=ooc, block_size=block_size)
    cube_info.print_report(print_function=print_function)
    stats_info.print_report(print_function=print_function)
    
def diff_files(filename_0, filename_1, shape, dtype=None, ooc=True, block_size=None, in_threshold=None, out_threshold=None):
    """diff_files(filename_0, filename_1, shape, dtype=None, ooc=True, block_size=None) -> DiffInfo object
    returns a DiffInfo about the content of 'filename_0' and 'filename_1', which are
    two cubes with 'shape'.
    If 'ooc' (out-of-core) is True, process 'block_size' elements at a time.
    """
    output_mode_callback()
    if ooc:
        diff_info = diff_info_ooc(filename_0, filename_1, shape=shape, dtype=dtype, block_size=block_size,
                                  in_threshold=in_threshold, out_threshold=out_threshold)
    else:
        cube_0 = fromfile_raw(filename_0, shape=shape, dtype=dtype)
        cube_1 = fromfile_raw(filename_1, shape=shape, dtype=dtype)
        diff_info = DiffInfo.diff_info(cube_0, cube_1,
                                       in_threshold=in_threshold, out_threshold=out_threshold)
    return diff_info

def print_diff_files(filename_0, filename_1, shape, dtype=None, ooc=True, block_size=None, in_threshold=None, out_threshold=None, print_function=None):
    """print_diff_files(filename_0, filename_1, shape, dtype=None, ooc=True, block_size=None, print_function=None)
    prints the DiffInfo about the content of 'filename_0' and 'filename_1', which are
    two cubes with 'shape'.
    If 'ooc' (out-of-core) is True, process 'block_size' elements at a time.
    """
    output_mode_callback()
    cube_info = CubeInfo(cube_shape=shape)
    diff_info = diff_files(filename_0, filename_1, shape=shape, dtype=dtype, ooc=ooc, block_size=block_size,
                           in_threshold=None, out_threshold=None)
    cube_info.print_report(print_function=print_function)
    diff_info.print_report(print_function=print_function)

def stats_info_ooc(filename, shape, dtype=None, block_size=None):
    def cumulate_stats_info(cubes, stats_info):
        #print cubes[0]
        stats_info += StatsInfo.stats_info(cubes[0])

    stats_info = StatsInfo()
    iterate_over_blocks(
        filenames=[filename],
        shape=shape,
        dtype=dtype,
        block_size=block_size,
        cumulate_function=cumulate_stats_info,
        cumulate_n_args={'stats_info': stats_info},
    )
    return stats_info

def diff_info_ooc(filename_0, filename_1, shape, dtype=None, block_size=None, in_threshold=None, out_threshold=None):
    def cumulate_diff_info(cubes, diff_info, in_threshold=None, out_threshold=None):
        diff_info += DiffInfo.diff_info(cubes[0], cubes[1], in_threshold=in_threshold, out_threshold=out_threshold)

    diff_info = DiffInfo()
    iterate_over_blocks(
        filenames=[filename_0, filename_1],
        shape=shape,
        dtype=dtype,
        block_size=block_size,
        cumulate_function=cumulate_diff_info,
        cumulate_n_args={'diff_info': diff_info,
                         'in_threshold': in_threshold,
                         'out_threshold': out_threshold
                        },
    )
    return diff_info
