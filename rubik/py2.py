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
           'lrange',
           'irange',
           'BASE_STRING',
           'StringIO',
           'get_input',
           'decode',
           'iteritems',
          ]

import sys

if sys.version_info[0] == 2: # pragma: no cover
    lrange = range

    irange = xrange

    from StringIO import StringIO

    BASE_STRING = basestring

    get_input = raw_input

    def decode(t):
        return t

    def iteritems(dct):
        return dct.iteritems()
