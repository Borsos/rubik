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

def flatten_list(sequence, depth=-1):
    out = []
    for item in sequence:
        if depth != 0 and isinstance(item, (list, tuple)):
            out.extend(flatten_list(item, depth - 1))
        else:
            out.append(item)
    return out

def flatten_tuple(sequence, depth=-1):
    return tuple(flatten_list(sequence, depth=depth))
