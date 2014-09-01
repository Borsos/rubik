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
import collections

from ..errors import RubikError
from ..shape import Shape
from .internals import output_mode_callback
from .comparison import reldiff_cube, absdiff_cube
from .input_output import fromfile_raw
from .out_of_core import BlockReader

def default_print_function(message):
    sys.stdout.write(message + '\n')

class InfoProgress(object):
    def __init__(self, info_obj, frequency=0.1, print_function=None):
        self.info_obj = info_obj
        if frequency is None:
            frequency = 0.1
        self.frequency = frequency
        if print_function is None:
            print_function = default_print_function
        self.print_function = print_function
        self._ns = set()

    def dump(self):
        fraction = self.info_obj.progress()
        if self.frequency > 0.0:
            n = int(fraction / self.frequency)
        else:
            n = sys.maxint
        if fraction == 1.0:
            dump = False
        elif 0.0 < fraction < 1.0:
            dump = n > 0 and not n in self._ns
        else:
            dump = False
        if dump:
            report = self.info_obj.report()
            self.print_function("=== {:%}".format(fraction))
            self.print_function(report)
            self.print_function('')
            self._ns.add(n)

class Info(object):
    KEYS = collections.OrderedDict()
    @classmethod
    def get_print_function(cls, print_function=None):
        if print_function is None:
            print_function = default_print_function
        return print_function

    @classmethod
    def op_min(cls, v0, v1):
        if v0[0] <= v1[0]:
            return v0
        else:
            return v1

    @classmethod
    def op_max(cls, v0, v1):
        if v0[0] >= v1[0]:
            return v0
        else:
            return v1

    @classmethod
    def get_op(cls, op, v0, v1):
        if v0[0] is None:
            return v1
        elif v1[0] is None:
            return v0
        else:
            return op(v0, v1)

    @classmethod
    def get_min(cls, v0, v1):
        return cls.get_op(cls.op_min, v0, v1)

    @classmethod
    def get_max(cls, v0, v1):
        return cls.get_op(cls.op_max, v0, v1)

    def print_report(self, print_function=None):
        print_function = self.get_print_function(print_function)
        print_function(self.report())
        
    def get_key_repr(self, key):
        get_key_method = getattr(self, 'get_{}'.format(key), None)
        if get_key_method is not None:
            return get_key_method()
        value = getattr(self, key)
        if isinstance(value, float):
            return '{:g}'.format(value)
        else:
            return repr(value)

    def report(self):
        return self.reports((self, ))

    @classmethod
    def reports(cls, instances, headers=None):
        if headers:
            headers = tuple(headers) + tuple("" for i in range(len(instances) - len(headers)))
        table = []
        if headers:
            table.append(("", ) + headers)
        for key, label in cls.KEYS.iteritems():
            row = [label, '=']
            empty = True
            for instance in instances:
                key_repr = instance.get_key_repr(key)
                if len(key_repr) > 0:
                    empty = False
                row.append(key_repr)
            if not empty:
                table.append(row)
        ln = [max(len(row[i]) for row in table) for i in range(len(instances) + 2)]
        f_list = []
        for lni in ln[:-1]:
            f_list.append("{{:{}s}}".format(lni))
        f_list.append("{}")
        fmt = ' '.join(f_list)
        return '\n'.join(fmt.format(*row) for row in table)

    def info_progress(self, frequency=None, print_function=None):
        return InfoProgress(self, frequency=frequency, print_function=print_function)

class StatsInfo(Info):
    """StatsInfo(...)
       collect statistics about a cube:
        o cube_name
        o cube_shape
        o cube_count
        o cube_sum
        o cube_ave
        o cube_min
        o cube_min_index
        o cube_max
        o cube_max_index
        o cube_count_zero
        o cube_count_nonzero
        o cube_count_nan
        o cube_count_inf
    """
    PERCENTAGE_FORMAT = '{:.2%}'
    KEYS = collections.OrderedDict((
        ('cube_name',			'name'),
        ('cube_shape',			'shape'),
        ('cube_count',			'#elements'),
        ('cube_percentage',		'%elements'),
        ('cube_min',			'min'),
        ('cube_min_index',		'min_index'),
        ('cube_max',			'max'),
        ('cube_max_index',		'max_index'),
        ('cube_sum',			'sum'),
        ('cube_ave',			'ave'),
        ('cube_count_zero',		'#zero'),
        ('cube_percentage_zero',	'%zero'),
        ('cube_count_nonzero',		'#nonzero'),
        ('cube_percentage_nonzero',	'%nonzero'),
        ('cube_count_nan',		'#nan'),
        ('cube_percentage_nan',		'%nan'),
        ('cube_count_inf',		'#inf'),
        ('cube_percentage_inf',		'%inf'),
    ))
    def __init__(self,
            cube_name="",
            cube_shape=Shape("0"),
            cube_offset=0,
            cube_count=0,
            cube_sum=0,
            cube_ave=None, 
            cube_min=None, 
            cube_min_index=None, 
            cube_max=None, 
            cube_max_index=None, 
            cube_count_zero=0,
            cube_count_nonzero=0,
            cube_count_nan=0,
            cube_count_inf=0):
        self.cube_name = cube_name
        self.cube_shape = cube_shape
        self.cube_offset = cube_offset
        self.cube_sum = cube_sum
        self.cube_count = cube_count
        self.cube_count_zero = cube_count_zero
        self.cube_count_nonzero = cube_count_nonzero
        self.cube_count_nan = cube_count_nan
        self.cube_count_inf = cube_count_inf
        self.cube_min = cube_min
        self.cube_min_index = cube_min_index
        self.cube_max = cube_max
        self.cube_max_index = cube_max_index

    def get_cube_shape(self):
        return str(self.cube_shape)

    def get_cube_percentage_zero(self):
        return self.PERCENTAGE_FORMAT.format(self.cube_fraction_zero)

    def get_cube_percentage_nonzero(self):
        return self.PERCENTAGE_FORMAT.format(self.cube_fraction_nonzero)

    def get_cube_percentage_inf(self):
        return self.PERCENTAGE_FORMAT.format(self.cube_fraction_inf)

    def get_cube_percentage_nan(self):
        return self.PERCENTAGE_FORMAT.format(self.cube_fraction_nan)

    def get_cube_percentage(self):
        return self.PERCENTAGE_FORMAT.format(self.cube_fraction)

    def get_cube_name(self):
        return self.cube_name

    @property
    def cube_fraction(self):
        total_count = self.cube_shape.count()
        if total_count == 0:
            return 0.0
        else:
            return self.cube_count / float(total_count)

    def progress(self):
        return self.cube_fraction

    @classmethod
    def stats_info(cls, cube, shape=None, offset=0):
        """stats_cube(cube, shape=None, offset=0) -> StatsInfo
           creates a StatsInfo object from a cube
        """
        if not isinstance(cube, np.ndarray):
            raise RubikError("cannot stat object of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))
        if shape is None:
            shape = cube.shape
        cube_shape = Shape(shape)
        cube_sum = cube.sum()
        cube_ave = None
        cube_count = cube.size
        if cube_count:
            cube_ave = cube_sum / float(cube_count)
        else:
            cube_ave = None
        cube_count_nonzero = np.count_nonzero(cube)
        cube_count_zero = cube_count - cube_count_nonzero
        cube_count_nan = np.count_nonzero(np.isnan(cube))
        cube_count_inf = np.count_nonzero(np.isinf(cube))
        cube_1d = cube.reshape((cube.size, ))
        cube_min_index = cube_1d.argmin()
        cube_min = cube_1d[cube_min_index]
        cube_max_index = cube_1d.argmax()
        cube_max = cube_1d[cube_max_index]
        cube_min_index = np.unravel_index(cube_min_index + offset, cube_shape)
        cube_max_index = np.unravel_index(cube_max_index + offset, cube_shape)
        stats_info = StatsInfo(
            cube_shape=cube_shape,
            cube_sum=cube_sum,
            cube_offset=offset,
            cube_count=cube_count,
            cube_min=cube_min,
            cube_min_index=cube_min_index,
            cube_max=cube_max,
            cube_max_index=cube_max_index,
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
        self.cube_offset = self.cube_count
        self.cube_count += stats_info.cube_count
        self.cube_count_zero += stats_info.cube_count_zero
        self.cube_count_nonzero += stats_info.cube_count_nonzero
        self.cube_count_nan += stats_info.cube_count_nan
        self.cube_count_inf += stats_info.cube_count_inf
        self.cube_min, self.cube_min_index = self.get_min(
            (self.cube_min, self.cube_min_index),
            (stats_info.cube_min, stats_info.cube_min_index))
        self.cube_max, self.cube_max_index = self.get_max(
            (self.cube_max, self.cube_max_index),
            (stats_info.cube_max, stats_info.cube_max_index))
        return self

    def __add__(self, stats_info):
        result = self.__class__()
        result += self
        result += stats_info
        return result

    def old_report(self):
        """report(self) -> StatsInfo report
        """

        return """\
shape         = {shape}
#elements     = {count}
min           = {min} [{min_index}]
max           = {max} [{max_index}]
sum           = {sum}
ave           = {ave}
#zero         = {count_zero} [{fraction_zero:.2%}]
#nonzero      = {count_nonzero} [{fraction_nonzero:.2%}]
#nan          = {count_nan} [{fraction_nan:.2%}]
#inf          = {count_inf} [{fraction_inf:.2%}]
""".format(
            shape=self.cube_shape,
            min=self.cube_min,
            min_index=self.cube_min_index,
            max=self.cube_max,
            max_index=self.cube_max_index,
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
        o left StatsInfo
        o right StatsInfo
        o rel_diff StatsInfo
        o abs_diff StatsInfo
    """
    def __init__(self,
        left=None,
        right=None,
        rel_diff=None,
        abs_diff=None,
        cube_shape=None,
        left_name="LEFT",
        rigth_name="RIGTH",
    ):
        def default_stats_info(obj, cube_name, cube_shape):
            if obj is None:
                return StatsInfo(cube_name=cube_name, cube_shape=cube_shape)
            else:
                return obj
        self.left = default_stats_info(left, cube_name=left_name, cube_shape=cube_shape)
        self.right = default_stats_info(right, cube_name=rigth_name, cube_shape=cube_shape)
        self.rel_diff = default_stats_info(rel_diff, cube_name="REL_DIFF", cube_shape=cube_shape)
        self.abs_diff = default_stats_info(abs_diff, cube_name="ABS_DIFF", cube_shape=cube_shape)

    def progress(self):
        return self.left.progress()

    def __iadd__(self, diff_info):
        self.left += diff_info.left
        self.right += diff_info.right
        self.rel_diff += diff_info.rel_diff
        self.abs_diff += diff_info.abs_diff
        return self

    def __add__(self, diff_info):
        result = self.__class__()
        result += self
        result += diff_info
        return result

    @classmethod
    def diff_info(cls, left, right, shape=None, offset=0, in_threshold=None, out_threshold=None):
        rel_diff_cube = reldiff_cube(left, right, in_threshold=in_threshold, out_threshold=out_threshold)
        abs_diff_cube = absdiff_cube(left, right, in_threshold=in_threshold, out_threshold=out_threshold)
        return cls(
            left=StatsInfo.stats_info(left, shape=shape, offset=offset),
            right=StatsInfo.stats_info(right, shape=shape, offset=offset),
            rel_diff=StatsInfo.stats_info(rel_diff_cube, shape=shape, offset=offset),
            abs_diff=StatsInfo.stats_info(abs_diff_cube, shape=shape, offset=offset),
        )

    def report(self):
        return StatsInfo.reports(
            instances=(self.left, self.right, self.rel_diff, self.abs_diff),
            )

diff_info = DiffInfo.diff_info

def print_stats(cube, print_function=None):
    """print_stats(cube, print_function=None)
    print statistics about cube
    """
    output_mode_callback()
    stats_info = StatsInfo.stats_info(cube)
    stats_info.print_report(print_function=print_function)
    
def print_diff(left, right, print_function=None):
    """print_diff(left, right, print_function=None)
    print statistics about left, right, and their diff
    """
    output_mode_callback()
    if left.cube_shape != right.cube_shape:
        raise RubikError("cannot diff cubes with different shape {} and {}".format(
            left.cube_shape,
            right.cube_shape,
        ))
    diff_info = DiffInfo.diff_info(left, right, in_threshold=in_threshold, out_threshold=out_threshold)
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
    stats_info = stats_file(filename, shape=shape, dtype=dtype, ooc=ooc, block_size=block_size)
    stats_info.print_report(print_function=print_function)
    
def diff_files(filename_l, filename_r, shape, dtype=None, ooc=True, block_size=None, max_memory=None, in_threshold=None, out_threshold=None):
    """diff_files(filename_l, filename_r, shape, dtype=None, ooc=True, block_size=None) -> DiffInfo object
    returns a DiffInfo about the content of 'filename_l' and 'filename_r', which are
    two cubes with 'shape'.
    If 'ooc' (out-of-core) is True, the overall memory size will be less than 'memory_size',
    and the memory size per block will be less than 'block_size'.
    By default, 'block_size' is '1gb', while 'max_memory' is not set.
    """
    output_mode_callback()
    if ooc:
        diff_info = diff_info_ooc(filename_l, filename_r, shape=shape, dtype=dtype,
                                  block_size=block_size, max_memory=max_memory,
                                  in_threshold=in_threshold, out_threshold=out_threshold)
    else:
        left = fromfile_raw(filename_l, shape=shape, dtype=dtype)
        right = fromfile_raw(filename_r, shape=shape, dtype=dtype)
        diff_info = DiffInfo.diff_info(left, right,
                                       in_threshold=in_threshold, out_threshold=out_threshold)
    return diff_info

def print_diff_files(filename_l, filename_r, shape, dtype=None, ooc=True, block_size=None, max_memory=None, in_threshold=None, out_threshold=None, print_function=None):
    """print_diff_files(filename_l, filename_r, shape, dtype=None, ooc=True, block_size=None, max_memory=None, print_function=None)
    prints the DiffInfo about the content of 'filename_l' and 'filename_r', which are
    two cubes with 'shape'.
    If 'ooc' (out-of-core) is True, the overall memory size will be less than 'memory_size',
    and the memory size per block will be less than 'block_size'.
    By default, 'block_size' is '1gb', while 'max_memory' is not set.
    """
    output_mode_callback()
    diff_info = diff_files(filename_l, filename_r, shape=shape, dtype=dtype, ooc=ooc,
                           block_size=block_size, max_memory=max_memory,
                           in_threshold=None, out_threshold=None)
    diff_info.print_report(print_function=print_function)

def stats_info_ooc(filename, shape, dtype=None, block_size=None, max_memory=None, update_frequency=None):
    def reduce_stats_info(cubes, stats_info, info_progress, shape):
        stats_info += StatsInfo.stats_info(cubes[0],
                                           shape, offset=stats_info.cube_count)
        info_progress.dump()

    stats_info = StatsInfo(cube_shape=shape)
    info_progress = stats_info.info_progress(frequency=update_frequency)
    block_reader = BlockReader(
        count=shape,
        dtype=dtype,
        block_size=block_size,
        max_memory=max_memory)
    block_reader.reduce(
        filenames=[filename],
        function=reduce_stats_info,
        shape=shape,
        info_progress=info_progress,
        stats_info=stats_info)
    return stats_info

def diff_info_ooc(filename_l, filename_r,
                  shape, dtype=None, block_size=None, max_memory=None,
                  update_frequency=None,
                  in_threshold=None, out_threshold=None):
    def reduce_diff_info(cubes, diff_info, shape, info_progress, in_threshold=None, out_threshold=None):
        diff_info += DiffInfo.diff_info(cubes[0], cubes[1],
                                        shape=shape, offset=diff_info.left.cube_count,
                                        in_threshold=in_threshold, out_threshold=out_threshold)
        info_progress.dump()

    diff_info = DiffInfo(cube_shape=shape)
    info_progress = diff_info.info_progress(frequency=update_frequency)
    block_reader = BlockReader(
        count=shape,
        dtype=dtype,
        block_size=block_size,
        max_memory=max_memory)
    block_reader.reduce(
        filenames=[filename_l, filename_r],
        function=reduce_diff_info,
        shape=shape,
        diff_info=diff_info,
        in_threshold=in_threshold,
        out_threshold=out_threshold,
        info_progress=info_progress,
    )
    return diff_info
