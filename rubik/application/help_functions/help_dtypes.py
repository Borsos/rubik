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
              'help_dtypes',
              'HelpDtypes',
          ]

from ... import conf

from .functor_help import Help

def help_dtypes(test=None, interactive=None, writer=None):
    HelpDtypes(test=test, interactive=interactive, writer=writer)()

class HelpDtypes(Help):
    def __call__(self):
        self.writer("""\
# Available data types

All numpy dtypes are valid data types.
You can set:
* the internal dtype, which is the default dtype;
* the specific dtype for each input file ('--input-dtype/-It');
* the specific dtype for each output file ('--output-dtype/-Ot');

This is the list of the available numpy dtypes:
""")
        for dtype_name, dtype_description in conf.DATA_TYPES.items():
            self.writer("{n:16s} {d}".format(n=dtype_name, d=dtype_description))

