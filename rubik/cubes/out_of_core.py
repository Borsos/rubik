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
           'BlockReader',
          ]

import numpy as np
import contextlib
import os

from ..errors import RubikError
from ..units import Memory
from ..shape import Shape
from ..conf import get_dtype
from .internals import get_default_dtype

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
    
class BlockReader(object):
    """BlockReader(...)
    A BlockReader object allows to read blocks from a list of files
    """
    DEFAULT_BLOCK_SIZE = Memory('1gb')
    def __init__(self, count, dtype=None, block_size=None, max_memory=None):
        if isinstance(count, Shape):
            count = count.count()
        if isinstance(count, (str, tuple)):
            count = Shape(count).count()
        self.count = count
        if dtype is None:
            dtype = get_default_dtype()
        else:
            dtype = get_dtype(dtype)
        self.dtype = dtype
        self.itemsize_b = dtype().itemsize
        if block_size is not None:
            block_size = Memory(block_size)
        self.block_size = block_size
        if max_memory is not None:
            max_memory = Memory(max_memory)
        self.max_memory = max_memory
        self.filesize_b = self.count * self.itemsize_b

    def check_files(self, filenames):
        """self.check_files(filenames) -> raise an exception if some file does
           not exists or has wrong size"""
        for filename in filenames:
            if not os.path.exists(filename):
                raise RubikError("file {} does not exists".format(filename))
            filesize_b = os.stat(filename).st_size
            if filesize_b != self.filesize_b:
                if filesize_b < self.filesize_b:
                    status = "short"
                else:
                    status = "long"
                raise RubikError("file {f}: too {s}: it contains {ci}/{cb} items/bytes, expected {ei}/{eb}".format(
                                 f=filename, 
                                 s=status,
                                 ci=filesize_b // self.itemsize_b,
                                 cb=filesize_b,
                                 ei=self.filesize_b // self.itemsize_b,
                                 eb=self.filesize_b))
        
    def read(self, filenames):
        """self.read(filenames) -> iterates over read blocks
           reads and yields blocks from filenames"""
        filenames = filelist(filenames)
        self.check_files(filenames)
        if not filenames:
            return
        if self.max_memory is None:
            max_memory_b = self.count * self.itemsize_b * len(filenames)
        else:
            max_memory_b = self.max_memory.get_bytes()
        if self.block_size is None:
            block_size_b = self.DEFAULT_BLOCK_SIZE.get_bytes()
        else:
            block_size_b = self.block_size.get_bytes()
        max_block_size_b = min(max_memory_b // len(filenames), block_size_b)
        block_count = max(1, max_block_size_b // self.itemsize_b)
        expected_count = self.count
        read_count = 0
        with multiopen(filenames, 'rb') as filehandles:
            while read_count < expected_count:
                blocks = []
                step_count = min(expected_count - read_count, block_count)
                if step_count == 0:
                    break 
                for filename, filehandle in zip(filenames, filehandles):
                    #print "reading {} items from {}".format(step_count, filename)
                    block = np.fromfile(filehandle, dtype=self.dtype, count=step_count)
                    if block.size < step_count:
                        raise RubikError("file {}: too short, read {} items, expected {}".format(
                                         filename, read_count + block.size, expected_count))
                    elif block.size < step_count:
                        raise RubikError("file {}: internal error, tring to read {} items, {} read".format(
                                         filename, step_count, block.size))
                    blocks.append(block)
                yield tuple(blocks)
                read_count += step_count
            for filename, filehandle in zip(filenames, filehandles):
                if filehandle.read(1):
                    raise RubikError("file {}: too long, read {} items, expected {}".format(
                                         filename, read_count + 1, expected_count))
 

    def reduce(self, filenames, function, *n_args, **p_args):
        """self.reduce(filenames, function, *n_args, **p_args) -> reduce result
        executes reduce 'function' on all the blocks read from 'filenames'.
        'function' is a function expecting a tuple of blocks as first arguments, 
        and *n_args, *p_args as following optional arguments.
        """
        result = None
        for blocks in self.read(filenames):
            result = function(blocks, *n_args, **p_args)
        return result

