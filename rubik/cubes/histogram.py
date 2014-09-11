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
           'histogram',
           'print_histogram',
          ]

import sys

import numpy as np

def histogram(cube, bins=10, hlength=80, hrange=None, decimals=None, fmt=None, mode=None):
    """histogram(cube, bins=10, hlength=80, hrange=None, decimals=None, fmt=None, mode=None) -> text lines
       Returns an ASCII representation of the histogram of cube
       * bins: number of bins
       * hlength: horizontal length of each histogram line
       * hrange: range of the histogram
       * decimals: number of decimals
       * fmt: line format
       * mode: 'number' or 'percentage', used if 'fmt' is None
    """
    if not isinstance(cube, np.ndarray):
        raise RubikError("cannot make an histogram from result of type {0}: it is not a numpy.ndarray".format(type(cube).__name__))

    if bins is None:
        bins = 10
    if fmt is None:
        if mode is None:
            mode is 'number'
        fmt_base = "{b}{s_start:{l_start}s}, {s_end:{l_end}s}{k}|{h}|"
        if mode == 'number':
            fmt = fmt_base + "{s_num:>{l_num}s}"
        elif mode == 'percentage':
            fmt = fmt_base + "{s_percentage:>{l_percentage}s}"
        else:
            raise ValueError("invalid mode {}: allowed modes are 'number', 'percentage'")

        fmt_base = "{b}{s_start:{l_start}s}, {s_end:{l_end}s}{k}|{h}|"
        fmt_percentage = fmt_base + "{s_percentage:>{l_percentage}s}"

    histogram, bins = np.histogram(cube, bins=bins, range=hrange)
    start = bins[0]
    d_min = None
    for end in bins[1:]:
        d = abs(end - start)
        if d_min is None or d < d_min:
            d_min = d
    if decimals is None:
        power = 0
        f_d_min = d_min - int(d_min)
        if f_d_min > 0:
            while True:
                if int(f_d_min * 10 ** power) > 0:
                    break
                power += 1
        else:
            power = 0
    else:
        power = decimals
    if power:
        fmt_float = "{{:.{power}f}}".format(power=power)
    else:
        fmt_float = "{{:f}}".format()
    start = bins[0]
    l = []
    num_max = 0
    l_num, l_percentage, l_start, l_end = 0, 0, 0, 0
    num_tot = histogram.sum()
    for num, end in zip(histogram, bins[1:]):
        s_num = str(num)
        fraction = float(num) / num_tot
        s_percentage = "{:.2%}".format(fraction)
        s_start = fmt_float.format(start)
        s_end = fmt_float.format(end)
        if len(s_num) > l_num:
            l_num = len(s_num)
        if len(s_percentage) > l_percentage:
            l_percentage = len(s_percentage)
        if len(s_start) > l_start:
            l_start = len(s_start)
        if len(s_end) > l_end:
            l_end = len(s_end)
        l.append((num, s_num, s_percentage, s_start, s_end))
        if num > num_max:
            num_max = num
        start = end
    
    fixed_text = fmt.format(
        b='[',
        s_start='',
        l_start=l_start,
        s_end='',
        l_end=l_end,
        k=']',
        h='',
        s_num='',
        l_num=l_num,
        s_percentage='',
        l_percentage=l_percentage)
    text_length = len(fixed_text)
    h_max = max(0, hlength - text_length)
    b = '['
    output_lines = []
    for c, (num, s_num, s_percentage, s_start, s_end) in enumerate(l):
        if c == len(l) - 1:
            k = ']'
        else:
            k = ')'
        l_l = int(0.5 + (h_max * num) / float(num_max))
        l_r = h_max - l_l
        h = '*' * l_l + ' ' * l_r
        output_lines.append(fmt.format(
            s_num=s_num,
            l_num=l_num,
            s_percentage=s_percentage,
            l_percentage=l_percentage,
            s_start=s_start,
            l_start=l_start,
            s_end=s_end,
            l_end=l_end,
            h=h,
            b=b,
            k=k,
        ))
    return output_lines

def print_histogram(cube, bins=10, hlength=80, hrange=None, decimals=None, fmt=None, mode=None, print_function=None):
    """print_histogram(cube, bins=10, hlength=80, hrange=None, decimals=None, fmt=None, mode=None, print_function=None)
       Prints an ASCII representation of the histogram of cube
       * bins: number of bins
       * hlength: horizontal length of each histogram line
       * hrange: range of the histogram
       * decimals: number of decimals
       * fmt: line format
       * mode: 'number' or 'percentage', used if 'fmt' is None
    """
    if print_function is None:
        print_function = lambda x: sys.stdout.write(x + '\n')
    for line in histogram(
           cube=cube,
           bins=bins,
           hlength=hlength,
           hrange=hrange,
           decimals=decimals,
           fmt=fmt,
           mode=mode):
       print_function(line)
