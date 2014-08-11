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

__all__ = ['format_filename',
          ]

from .shape import Shape

def format_filename(filename, shape, file_format, file_dtype, keywords=None):
    if keywords is None:
        keywords = {}
    count = 0
    if shape:
        count = 1
        for i in shape:
            count *= i
    else:
        count = 0
    if not isinstance(shape, Shape):
        shape = Shape(shape)
    return filename.format(
        shape=shape,
        rank=len(shape),
        count=count,
        format=file_format,
        dtype=file_dtype.__name__,
        **keywords
    )
