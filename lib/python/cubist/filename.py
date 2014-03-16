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

import re

from .errors import CubistError

class Filename(object):
    def __init__(self, init):
        if isinstance(init, Filename):
            filename = init._filename
        elif isinstance(init, str):
            filename = self._from_string(init)
        else:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=self.__class__.__name__,
                t=type(init).__name__,
                o=init))
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def __str__(self):
        return self._filename

    def __repr__(self):
        return "{0}(filename={1!r})".format(self.__class__.__name__, self._filename)

    @classmethod
    def _from_string(cls, value):
        return value
            

class InputFilename(Filename):
    pass

class OutputFilename(Filename):
    pass