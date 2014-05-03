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

__all__ = ['not_equals_cube', 'not_equals_num', 'not_equals',
           'equals_cube', 'equals_num', 'equals',
           'reldiff_cube', 'threshold_cube',
           'absdiff_cube', 'abs_threshold_cube',
           'where_indices',
           'nonzero_cube']

import numpy as np

from .settings import *

def not_equals_cube(cube_0, cube_1, tolerance=0.0):
    """not_equals_cube(cube_0, cube_1, tolerance=0.0) -> a cube with 1.0 where
           cube_0 != cube_1 within the given tolerance, 0.0 elsewhere
    """
    c = (np.abs(cube_0 - cube_1) > tolerance).astype(cube_0.dtype)
    return c

def not_equals_num(cube_0, cube_1, tolerance=0.0):
    """not_equals_num(cube_0, cube_1, tolerance=0.0) -> the number of elements
           that are != within the given tolerance
    """
    c = np.count_nonzero(not_equals_cube(cube_0, cube_1, tolerance))
    return c

def equals_cube(cube_0, cube_1, tolerance=0.0):
    """not_equals_cube(cube_0, cube_1, tolerance=0.0) -> a cube with 1.0 where
           cube_0 == cube_1 within the given tolerance, 0.0 elsewhere
    """
    c = (np.abs(cube_0 - cube_1) <= tolerance).astype(cube_0.dtype)
    return c

def equals_num(cube_0, cube_1, tolerance=0.0):
    """num__equals(cube_0, cube_1, tolerance=0.0) -> the number of elements
           that are == within the given tolerance
    """
    c = np.count_nonzero(equals_cube(cube_0, cube_1, tolerance))
    return c

def not_equals(cube_0, cube_1, tolerance=0.0):
    """not_equals(cube_0, cube_1, tolerance=0.0) -> True if cube_0 == cube_1
           within the given tolerance, False otherwise
    """
    return not_equals_num(cube_0, cube_1, tolerance) != 0


def equals(cube_0, cube_1, tolerance=0.0):
    """equals(cube_0, cube_1, tolerance=0.0) -> True if cube_0 == cube_1
           within the given tolerance, False otherwise
    """
    return not_equals_num(cube_0, cube_1, tolerance) == 0

def threshold_cube(cube, threshold=0.0, value=0.0):
    """threshold_cube(cube, threshold=0.0, value=0.0) : sets to 'value' all elements <= 'threshold'
    """
    return np.where(cube > threshold, cube, value)

def abs_threshold_cube(cube, threshold=0.0, value=0.0):
    """abs_threshold_cube(cube, threshold=0.0, value=0.0) : sets to 'value' all elements 
    whose absolute value <= 'threshold'
    """
    return np.where(np.abs(cube) > threshold, cube, value)

def absdiff_cube(cube_0, cube_1, in_threshold=None, out_threshold=None, percentage=False):
    """absdiff(cube_0, cube_1, in_threshold=None, out_threshold=None) ->
    cube of absolute difference
    | a - b |
    'in_threshold': if passed, this absolute threshold is applied to 'a' and 'b';
    'out_threshold': if passed, this absolute threshold is applied to the output (the absdiff)
    """
    if in_threshold is not None:
        cube_0 = abs_threshold_cube(cube_0, threshold=in_threshold)
        cube_1 = abs_threshold_cube(cube_1, threshold=in_threshold)
    cube_out = np.nan_to_num(np.abs(cube_0 - cube_1))
    if out_threshold is not None:
        cube_out = abs_threshold_cube(cube_out, threshold=out_threshold)
    return cube_out

def reldiff_cube(cube_0, cube_1, in_threshold=None, out_threshold=None, percentage=False):
    """reldiff(cube_0, cube_1, in_threshold=None, out_threshold=None, percentage=False) ->
    cube of relative difference
    | a - b |
    _________
       |a|
    'in_threshold': if passed, this absolute threshold is applied to 'a' and 'b';
    'out_threshold': if passed, this absolute threshold is applied to the output (the reldiff)
    'percentage': if True, the output is multiplied by 100.0
    """
    if in_threshold is not None:
        cube_0 = abs_threshold_cube(cube_0, threshold=in_threshold)
        cube_1 = abs_threshold_cube(cube_1, threshold=in_threshold)
    cube_out = np.nan_to_num(np.abs(cube_0 - cube_1) / np.abs(cube_0))
    if out_threshold is not None:
        cube_out = abs_threshold_cube(cube_out, threshold=out_threshold)
    if percentage:
        cube_out *= 100.0
    return cube_out

def nonzero_cube(cube, tolerance=0.0):
    """nonzero_cube(cube_in, tolerance=0.0) -> a cube with 0.0 where cube_in == 0.0 within
    the given tolerance, 1.0 elsewhere"""
    if tolerance:
        return (np.abs(cube) > tolerance).astype(DEFAULT_DTYPE)
    else:
        return (cube != 0).astype(DEFAULT_DTYPE)

def where_indices(cube, condition=None):
    """where_indices(cube, condition=None) -> returns an array containing of all the coordinates and
    the value where the cube 'condition' evaluates to True; if 'condition' is None, it is set to
    cube:
    >>> a = np.eye(3)
    >>> print cb.where_indices(a)
    [[ 0.  0.  1.]
     [ 1.  1.  1.]
     [ 2.  2.  1.]]
    >>> print cb.where_indices(a, a == 0)
    [[ 0.  1.  0.]
     [ 0.  2.  0.]
     [ 1.  0.  0.]
     [ 1.  2.  0.]
     [ 2.  0.  0.]
     [ 2.  1.  0.]]
    >>> 
    """
    if condition is None:
        condition = cube
    indices = np.where(condition)
    result = np.array(indices + (np.fromiter((cube[index] for index in zip(*indices)), cube.dtype), ))
    return result.T
    
