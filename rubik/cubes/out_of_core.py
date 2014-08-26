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
           'filelist',
           'multiopen',
           'iterate_over_blocks',
          ]

import numpy as np
import contextlib
from ..errors import RubikError
from ..units import Memory
from ..shape import Shape
from ..conf import get_dtype
from .settings import DEFAULT_DTYPE

def filelist(filenames):
    if isinstance(filenames, str):
        filenames = (filenames, )
    elif isinstance(filenames, (list, tuple)):
        filenames = tuple(filenames)
    else:
        raise TypeError("invalid filename value {!r} of type {}: it must be str, tuple or list".format(filename, type(filename).__name__))
    return filenames

@contextlib.contextmanager
def multiopen(filenames, mode):
    filenames = filelist(filenames)
    filehandles = tuple(open(filename, mode) for filename in filenames)
    yield filehandles
    for filehandle in filehandles:
        filehandle.close()
    
def iterate_over_blocks(filenames, shape, cumulate_function, dtype=None, block_size=None, cumulate_p_args=None, cumulate_n_args=None):
    filenames = filelist(filenames)
    if not filenames:
        return
    if block_size is None:
        block_size = Memory('1gb')
    elif not isinstance(block_size, Memory):
        block_size = Memory(block_size)
    block_size_b = block_size.get_bytes()
    if not isinstance(shape, Shape):
        shape = Shape(shape)
    if dtype is None:
        dtype = DEFAULT_DTYPE
    else:
        dtype = get_dtype(dtype)
    if cumulate_n_args is None:
        cumulate_n_args = {}
    if cumulate_p_args is None:
        cumulate_p_args = {}
    expected_count = shape.count()
    itemsize_b = dtype().itemsize
    block_count = max(1, block_size_b // (itemsize_b * len(filenames)))
    read_count = 0
    with multiopen(filenames, 'rb') as filehandles:
        while read_count < expected_count:
            blocks = []
            step_count = min(expected_count - read_count, block_count)
            if step_count == 0:
                break 
            for filename, filehandle in zip(filenames, filehandles):
                #print "reading {} items from {}".format(step_count, filename)
                block = np.fromfile(filehandle, dtype=dtype, count=step_count)
                if block.size < step_count:
                    raise RubikError("file {}: too short, read {} items, expected {}".format(filename, read_count + block.size, expected_count))
                elif block.size < step_count:
                    raise RubikError("file {}: internal error, tring to read {} items, {} read".format(filename, step_count, block.size))
                blocks.append(block)
            cumulate_function(blocks, *cumulate_p_args, **cumulate_n_args)
            read_count += step_count
        for filename, filehandle in zip(filenames, filehandles):
            if filehandle.read(1):
                raise RubikError("file {}: too long, read {} items, expected {}".format(filename, read_count + 1, expected_count))
 
        
 
        
    
    
