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
    __prefix__ = 'x'
    __filenames__ = {}
    __re_split__ = re.compile("^([a-zA-Z]+\w+)\@(.*)")
    def __init__(self, init):
        varname = None
        if isinstance(init, Filename):
            filename = init._filename
        elif isinstance(init, (list, tuple)) and len(init) == 2:
            varname, filename = self._from_string(init)
        elif isinstance(init, str):
            varname, filename = self._from_string(init)
        else:
            raise ValueError("cannot make a {c} from {t} object {o!r}".format(
                c=self.__class__.__name__,
                t=type(init).__name__,
                o=init))
        self._filename = filename
        self._varname = varname
        self.__class__.register(self)

    @classmethod
    def register(cls, filename_instance):
        if filename_instance._varname is None:
            filename_instance._varname = "{0}{1}".format(cls.__prefix__, len(cls.__filenames__))
        if filename_instance._varname in cls.__filenames__:
            raise CubistError("invalid filename {0}@{1}: varname {0} already in use".format(filename_instance._varname, filename_instance._filename))
        cls.__filenames__[filename_instance._varname] = filename_instance

    @property
    def filename(self):
        return self._filename

    @property
    def varname(self):
        return self._varname

    def __str__(self):
        return "{0}@{1}".format(self._varname, self._filename)

    def __repr__(self):
        return "{0}(varname={1!r}, filename={2!r})".format(self.__class__.__name__, self._varname, self._filename)

    @classmethod
    def _from_string(cls, value):
        m = cls.__re_split__.match(value)
        if m:
            return m.groups()
        else:
            return None, value
            

class InputFilename(Filename):
    __prefix__ = 'i'
    __filenames__ = {}

class OutputFilename(Filename):
    __prefix__ = 'o'
    __filenames__ = {}
