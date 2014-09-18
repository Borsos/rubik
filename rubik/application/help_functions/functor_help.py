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

from ..log import get_print

class Help(object):
    DEFAULT_TEST = False
    DEFAULT_INTERACTIVE = False
    def __init__(self, test=False, interactive=False, writer=None):
        if test is None:
            test = self.DEFAULT_TEST
        self.test = test
        if interactive is None:
            interactive = self.DEFAULT_INTERACTIVE
        self.interactive = interactive
        if writer is None:
            writer = get_print()
        self.writer = writer

    def __call__(self):
        raise NotImplementedError("Help.__call__")

