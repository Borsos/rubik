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
           'RubikTestSuite',
          ]


import unittest
import tempfile
import shutil
import fnmatch
import sys
import os

class RubikTestSuite(unittest.TestSuite):
    def __init__(self, suite_name, *n_args, **p_args):
        super(RubikTestSuite, self).__init__(*n_args, **p_args)
        self._registered_test_classes = []
        self.suite_name = suite_name

    def run(self, result):
        tmpdir = tempfile.mkdtemp()
        try:
            os.chdir(tmpdir)
            super(RubikTestSuite, self).run(result)
        finally:
            shutil.rmtree(tmpdir)
        
    def register_test_class(self, test_class):
        self._registered_test_classes.append(test_class)

    def test_classes_and_names(self):
        for test_class in self._registered_test_classes:
            for test_name in test_class.test_names():
                yield test_class, "{}.{}".format(self.suite_name, test_name)
        
    def test_names(self):
        for test_class, test_name in self.test_classes_and_names():
            yield test_name
        

    
    
