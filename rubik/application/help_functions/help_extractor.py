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
              'help_extractor',
              'HelpExtractor',
          ]

from .functor_help_text import HelpText

def help_extractor(test=None, interactive=None, writer=None):
    HelpExtractor(test=test, interactive=interactive, writer=writer)()

class HelpExtractor(HelpText):
    TEXT = """\
# Extractors

An extractor can be associated to each input file to read only a portion of that
file. Due to memory opimization, only the portion is read, so there is no need
to temporarily store the entire file. This means that if you want to read only a
subcube from a huge file, you will use memory only for the subcube.

Extractors are lists of index selectors separated by 'x' or ','.

Each input file can have a specific extractor. The shape and the extractor must
have the same rank.

Each index selector can be:
* a python slice [start:]stop[:step], for instance
  - ':' -> select all indices
  - '1:' -> select all indices but the first
  - ':-3' -> select all indices but the last three
  - '::2' -> select from the first to the last indices with stride 2
* an integer number; in this case, only the corresponding index is selected on
  that dimension, and the dimension is skipped in the output.

For instance, if the shape is '8x1000x30':
* '-x :x0x:' will extract the subcube '8x30' corresponding to the plane with 0
  on the second dimension
* '-x 3:x8:10x:5' will extract a subcube '5x2x5' (remember that, in a python
  slice, the start is always included and the stop is always excluded.
"""
