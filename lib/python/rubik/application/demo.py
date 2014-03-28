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
import shlex

from .log import PRINT
from ..py23 import get_input
from ..errors import RubikTestError

class Text(object):
    TEXT_WRAPPER = textwrap.TextWrapper(initial_indent='', drop_whitespace=True, replace_whitespace=True, fix_sentence_endings=True)
    RE_ESCAPED_NEWLINES = re.compile('\\\\\n')
    RE_CONTINUATION = re.compile(r"^.*(?<!\\)\\$")
    RE_WHITESPACES = re.compile(r"\s+")
    def __init__(self, parent, text=None):
        self._parent = parent
        self._child = None
        if self._parent is not None:
            self._parent._child = self
        self._lines = []
        if text:
            self._lines.append(text)

    def get_mode(self):
        return 'default'

    def requires(self):
        return False

    def accepts(self):
        return False

    def add(self, text):
        self._lines.append(text)

    @classmethod
    def remove_escaped_newlines(cls, text):
        return cls.RE_ESCAPED_NEWLINES.sub('', text)

    @classmethod
    def fill_text(cls, text):
        text = cls.RE_WHITESPACES.sub(' ', text.strip())
        return cls.TEXT_WRAPPER.fill(text)

    def get_text(self):
        return '\n'.join(self._lines)

class Paragraph(Text):
    def accepts(self):
        if len(self._lines) >= 2:
            return len(self._lines[-1]) != 0 and len(self._lines[-2]) != 0
        else:
            return True

    def get_text(self):
        while self._lines:
            if not self._lines[-1]:
                self._lines.pop(-1)
            else:
                break
        if self._lines:
            return self.fill_text('\n'.join(self._lines)) + '\n'
        else:
            return None

class Header(Text):
    def __init__(self, parent, heading, text):
        self._heading = heading
        super(Header, self).__init__(parent, text)

    def requires(self):
        return self.RE_CONTINUATION.match(self._lines[-1]) is not None

    def get_text(self):
        text = '\n'.join(self._lines)
        return self._heading + ' ' + self.fill_text(self.remove_escaped_newlines(text)) + '\n'

class Command(Text):
    def __init__(self, parent, heading, text):
        self._heading = heading
        super(Command, self).__init__(parent, text)

    def requires(self):
        return self.RE_CONTINUATION.match(self._lines[-1]) is not None

    def get_mode(self):
        return 'result'

    def get_text(self):
        return '\n' + self._heading + ' ' + self.get_command()

    def get_command(self):
        return '\n'.join(self._lines)

class Result(Text):
    def accepts(self):
        return True
    
    def get_text(self):
        text = super(Result, self).get_text()
        command = self._parent.get_command()
        command = self.remove_escaped_newlines(command)
        command_line = shlex.split(command)
        process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = process.communicate()[0].rstrip('\n')
        if output != text:
            PRINT("expected output is <<<\n{0}\n>>>".format(text))
            PRINT("actual   output is <<<\n{0}\n>>>".format(output))
            raise RubikTestError("demo test failed")
        if text:
            text += '\n'
        return text + '$\n'

class Interface(object):
    RE_SPECIAL_LINE = re.compile(r"^(#+|\$)\s+(.*)$")
    RE_END_RESULT = re.compile("^\$\s*$")
    def __init__(self):
        pass

    def ask(self, message):
        return get_input(message)
        
    def press_enter(self):
        return self.ask("Press ENTER...")

    @classmethod
    def split(cls, text):
        prev = None
        continuation = False
        mode = 'default'
        for line in text.split('\n'):
            #print "@@@", mode, prev, repr(line)
            if prev is not None and prev.requires():
                prev.add(line)
            else:
                if mode == 'default':
                    m = cls.RE_SPECIAL_LINE.match(line)
                    if m:
                        if prev is not None:
                            yield prev.get_text()
                            mode = prev.get_mode()
                        t, content = m.groups()
                        if t.startswith('#'):
                            prev = Header(prev, t, content)
                        elif t.startswith('$'):
                            prev = Command(prev, t, content)
                    else:
                        if prev is None:
                            prev = Paragraph(prev, line)
                        else:
                            if prev.accepts():
                                prev.add(line)
                            else:
                                yield prev.get_text()
                                mode = prev.get_mode()
                                if mode == 'result':
                                    m = cls.RE_END_RESULT.match(line)
                                    if m:
                                        prev = Result(prev, None)
                                        yield prev.get_text()
                                        mode = prev.get_mode()
                                        prev = None
                                    else:
                                        prev = Result(prev, line)
                                else:
                                    prev = Paragraph(prev, line)
                elif mode == 'result':
                    m = cls.RE_END_RESULT.match(line)
                    if m:
                        yield prev.get_text()
                        mode = prev.get_mode()
                        prev = None
                        continue
                    else:
                        prev.add(line)
        if prev is not None:
            yield prev.get_text()
            mode = prev.get_mode()

    def show_text(self, text):
        for t in self.split(text):
            if t is not None:
                PRINT(t)

class Demo(Interface):
    def __init__(self):
        pass

    def run(self, text):
        self.show_text(text)

def demo_runner(text):
    demo = Demo()
    demo.run(text)
