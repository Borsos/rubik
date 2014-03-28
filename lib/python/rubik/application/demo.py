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

import re
import textwrap
import subprocess

from .log import PRINT
from ..py23 import get_input
from ..errors import RubikTestError

class Interface(object):
    RE_HEADER = re.compile(r"^(\#+)\s(.*)$")
    RE_PARAGRAPH_SPLIT = re.compile(r"\n\n")
    def __init__(self):
        pass

    def ask(self, message):
        return get_input(message)
        
    def press_enter(self):
        return self.ask("Press ENTER...")

    @classmethod
    def split(cls, text):
        begin, end = 0, 0
        for m in cls.RE_HEADER.finditer(text):
            print m
            b, e = m.span()
            if b > begin:
                for text in cls.split_paragraph(text[:b]):
                    yield text + '\n'
            begin = b
            end = e
            yield "\n>>>{0} {1}\n".format(m.groups())
        if end < len(text):
            for text in cls.split_paragraph(text[end:]):
                yield text
 

    @classmethod
    def split_paragraph(cls, paragraph):
        for text in cls.RE_PARAGRAPH_SPLIT.split(paragraph):
            yield cls.wrap_paragraph(text)
        
    @classmethod
    def wrap_paragraph(cls, text):
        return textwrap.fill(text)

    def show_text(self, text):
        for t in self.split(text):
            PRINT(t)

class Demo(Interface):
    RE_SPACES = re.compile("\s+")
    def __init__(self):
        pass

    @classmethod
    def iter_args(cls, command_line):
        for item in command_line:
            if cls.RE_SPACES.match(item):
                yield repr(item)
            else:
                yield item

    @classmethod
    def repr_command_line(cls, command_line):
        return ' '.join(cls.iter_args(command_line))

    def run_command(self, command_line, expected_output=None, should_fail=False, expected_returncode=None):
        PRINT("$ {0}".format(self.repr_command_line(command_line)))
        process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = process.communicate()[0]
        PRINT(output)
        PRINT("$")
        returncode = process.returncode
        if expected_output is not None and expected_output != output:
            raise RubikTestError("output does not match")
        if expected_returncode is not None and expected_returncode != returncode:
            raise RubikTestError("returncode does not match [{0} != {1}]".format(returncode, expected_returncode))
        if should_fail and returncode == 0:
            raise RubikTestError("test should fail, but does not fail")
        elif (not should_fail) and returncode != 0:
            raise RubikTestError("test failed")

    def run(self):
        raise NotImplementedError()
