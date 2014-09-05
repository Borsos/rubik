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

import os
import shutil
import tempfile
import contextlib

class TempDirInfo(object):
    def __init__(self, dirname, clear=True):
        self.dirname = dirname
        self.clear = clear

    def __str__(self):
        return "{}(dirname={!r}, clear={!r})".format(self.__class__.__name__, self.dirname, self.clear)

    __repr__ = __str__
 
@contextlib.contextmanager
def chtempdir(suffix='', prefix='tmp', dir=None, clear=True):
    old_pwd = os.getcwd()
    dirname = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    os.chdir(dirname)
    temp_dir_info = TempDirInfo(dirname=dirname, clear=clear)
    yield temp_dir_info
    os.chdir(old_pwd)
    if temp_dir_info.clear:
        shutil.rmtree(dirname)
    
