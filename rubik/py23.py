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

import sys

if sys.version_info.major == 2:
    PY3 = False
else:
    PY3 = True

if PY3:
    def lrange(*n_args, **p_args):
        return list(range(*n_args, **p_args))
    irange = range
else:
    lrange = range
    irange = xrange

if PY3:
    get_input = input
    def decode(b):
        return b.decode('utf8')
else:
    get_input = raw_input
    def decode(t):
        return t
