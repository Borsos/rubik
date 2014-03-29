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
import shlex
import difflib
import textwrap
import subprocess
import collections

from .log import PRINT
from .. import py23
from ..errors import RubikTestError, RubikError

MatchResult = collections.namedtuple('MatchResult', ('match_type', 'match'))

class Visitor(object):
    def visit(self, node):
        raise NotImplementedError("{0}.visit(self, node)".format(self.__class__.__name__))

class TestVisitor(Visitor):
    def visit(self, node):
        node.test()

class OutVisitor(Visitor):
    def __init__(self, test=False, interactive=False, writer=PRINT):
        self.test = test
        self.writer = writer
        self.interactive = interactive

class ShowVisitor(OutVisitor):
    def visit(self, node):
        node.show(test=self.test, interactive=self.interactive, writer=self.writer)

class DumpVisitor(OutVisitor):
    def visit(self, node):
        node.dump(test=self.test, interactive=self.interactive, writer=self.writer)

class ExampleError(RubikError):
    pass

class Example(object):
    def __init__(self, text=None):
        if text is not None:
            self.set_text(text)

    def set_text(self, text):
        self._root = Paragraph(None)
        self._text = text
        self._lines = text.split('\n')
        self._lines.reverse()
        self._line_number = 0
        self._root.parse(self)
        return self._root

    def test(self):
        test_visitor = TestVisitor()
        self._root.accept(test_visitor)

    def dump(self, test=False, interactive=False, writer=None):
        dump_visitor = DumpVisitor(test=test, interactive=interactive, writer=writer)
        self._root.accept(dump_visitor)

    def show(self, test=False, interactive=False, writer=None):
        show_visitor = ShowVisitor(test=test, interactive=interactive, writer=writer)
        self._root.accept(show_visitor)

    def pop(self):
        line = self._lines.pop(-1)
        self._line_number += 1
        return self._line_number, line

    def push(self, line):
        self._line_number -= 1
        self._lines.append(line)

    def len(self):
        return len(self._lines)

    def __tobool(self):
        return len(self._lines) != 0

    if py23.PY3:
        __bool__ = __tobool
    else:
        __nonzero__ = __tobool

class Node(object):
    TEXT_WRAPPER = textwrap.TextWrapper(initial_indent='', drop_whitespace=True, replace_whitespace=True, fix_sentence_endings=True)
    RE_ESCAPED_NEWLINES = re.compile('\\\\\n')
    RE_WHITESPACES = re.compile(r"\s+")

    __pre_node_classes__ = []
    __post_node_classes__ = []
    __default_node_class__ = None
    __res__ = {}
    __re_continuation__ = re.compile(r"^.*(?<!\\)\\$")
    def __init__(self, parent):
        self._parent = parent
        self._child = None
        if self._parent is not None:
            self._parent._child = self
        self._lines = []
        self._continued = False

    def _default_node(self):
        if self._continued:
            return self
        else:
            return self.__default_node_class__(self)

    def test(self):
        pass

    def render(self, interactive=False):
        return self.get_text()

    def dump(self, test=False, interactive=False, writer=None):
        if writer is None:
            writer = PRINT
        text = self.render(interactive=interactive)
        indentation = "  "
        if text is None:
            text = ''
        else:
            text = self.indent(self.get_text(), indentation) + '\n'
        writer("<<<{0}>>>{{\n{1}}}".format(self.__class__.__name__, text))
        if test:
            self.test()

    def show(self, test=False, interactive=False, writer=None):
        if writer is None:
            writer = PRINT
        text = self.render(interactive=interactive)
        if text is not None:
            writer(text)
        if test:
            self.test()

    def accept(self, visitor):
        visitor.visit(self)
        node = self._child
        while node:
            visitor.visit(node)
            node = node._child

    @property
    def parent(self):
        return self._parent

    @property
    def child(self):
        return self._child

    @classmethod
    def remove_escaped_newlines(cls, text):
        return cls.RE_ESCAPED_NEWLINES.sub('', text)

    @classmethod
    def fill_text(cls, text):
        text = cls.RE_WHITESPACES.sub(' ', text.strip())
        return cls.TEXT_WRAPPER.fill(text)

    @classmethod
    def indent(cls, text, indentation):
        return '\n'.join(indentation + line for line in text.split('\n'))
    
    def get_text(self):
        return '\n'.join(line for line_number, line in self._lines)

    @classmethod
    def set_default_node_class(cls, node_class):
        cls.__default_node_class__ = node_class

    @classmethod
    def add_pre_node_classes(cls, *node_classes):
        for node_class in node_classes:
            cls.__pre_node_classes__.append(node_class)

    @classmethod
    def add_post_node_classes(cls, *node_classes):
        for node_class in node_classes:
            cls.__post_node_classes__.append(node_class)

    def set_continued(self, line):
        self._continued = bool(self.__re_continuation__.match(line))

    def add_line(self, line_number, line):
        self.set_continued(line)
        self._lines.append((line_number, line))

    def parse(self, example):
        assert isinstance(example, Example)
        parser = self
        while example:
            line_number, line = example.pop()
            parser = parser.parse_line(line_number, line)
            if parser is None:
                raise ExampleError("{0}: unparsed line #{1} {2!r}".format(self.__class__.__name__, line_number, line))
        if example:
            raise ExampleError("{0}: left {1} unparsed lines".format(self.__class__.__name__, len(example)))

    @classmethod
    def matches_line(cls, line_number, line):
        for match_type, match_re in cls.__res__.items():
            match = match_re.match(line)
            if match:
                return MatchResult(match_type=match_type, match=match)
        else:
            return None
        
    def parse_match_result(self, line_number, line, match_result):
        raise NotImplementedError("{0}.parse_match_result(self, line_number, line, match_result)".format(self.__class__.__name__))
        
    def parse_line(self, line_number, line):
        #print "@@@ {:2d} {!r}".format(line_number, line)
        if self._continued:
            self.add_line(line_number, line)
            return self

        # pre nodes
        for pre_node_class in self.__pre_node_classes__:
            match_result = pre_node_class.matches_line(line_number, line)
            #print "pre", self.__class__, pre_node_class, match_result
            if match_result:
                pre_node = pre_node_class(self)
                return pre_node.parse_match_result(line_number, line, match_result)
        else:
            match_result = self.matches_line(line_number, line)
            #print "----", self.__class__, self.__class__, match_result
            if match_result:
                return self.parse_match_result(line_number, line, match_result)
        
        # post nodes
        for post_node_class in self.__post_node_classes__:
            match_result = post_node_class.matches_line(line_number, line)
            #print "post", self.__class__, post_node_class, match_result
            if match_result:
                post_node = post_node_class(self)
                return post_node.parse_match_result(line_number, line, match_result)

        raise ExampleError("{0}: line #{1} {2!r} cannot be parsed".format(self.__class__.__name__, line_number, line))
        

class WrappedText(Node):
    def get_text(self):
        for extr in 0, -1:
            while self._lines:
                if not self._lines[extr][-1]:
                    self._lines.pop(extr)
                else:
                    break
        if self._lines:
            text = self.remove_escaped_newlines(super(WrappedText, self).get_text())
            return self.fill_text(text) + '\n'
        else:
            return None

class Header(WrappedText):
    __pre_node_classes__ = []
    __post_node_classes__ = []
    __res__ = {
        'header': re.compile(r"(^\#+)\s+(.*)$"),
    }
    def __init__(self, parent):
        super(Header, self).__init__(parent)
        self._heading = None

    def parse_match_result(self, line_number, line, match_result):
        self._heading, line = match_result.match.groups()
        self.add_line(line_number, self._heading + ' ' + line)
        return self._default_node()
        
class Result(Node):
    __pre_node_classes__ = []
    __post_node_classes__ = []
    __res__ = {
        'result': re.compile(r"^([^\$].*|)$"),
        'end_result': re.compile(r"\$\s*$"),
    }
    def parse_match_result(self, line_number, line, match_result):
        if match_result.match_type == 'result':
            self.add_line(line_number, match_result.match.groups()[-1])
            return self
        elif match_result.match_type == 'end_result':
            return self._default_node()

    def get_result(self):
        return super(Result, self).get_text()

    def get_text(self):
        if not self._lines:
            if not isinstance(self._child, Command):
                return '$\n'
            else:
                return None
        else:
            text = self.get_result()
            if not isinstance(self._child, Command):
                text += '\n$'
            return text + '\n'

class Command(Node):
    __pre_node_classes__ = []
    __post_node_classes__ = []
    __res__ = {
        'command': re.compile(r"(^\$)\s+(.*)$"),
    }
    def parse_match_result(self, line_number, line, match_result):
        self.add_line(line_number, match_result.match.groups()[-1])
        return self._default_node()
        
    def get_command(self):
        return self.remove_escaped_newlines(super(Command, self).get_text())

    def get_text(self):
        lines = ["$ " + self._lines[0][-1]]
        lines.extend(line for line_number, line in self._lines[1:])
        return '\n'.join(lines)

    def test(self):
        command = self.get_command()
        command_line = shlex.split(command)
        if isinstance(self._child, Result):
            expected_output = self._child.get_result()
        else:
            expected_output = ""
        process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        actual_output = py23.decode(process.communicate()[0]).rstrip('\n')
        if actual_output != expected_output:
            #PRINT("executed command = {0!r}".format(command))
            #PRINT("expected_output = {{\n{0}\n}}\nactual_output = {{\n{1}\n}}".format(
            #    expected_output,
            #    actual_output))
            for line in difflib.unified_diff(
                    expected_output.split('\n'),
                    actual_output.split('\n'),
                    fromfile='excected_output',
                    tofile='actual_output',
                    n=max(len(expected_output),
                    len(actual_output)), lineterm=''):
                PRINT(line)
            raise RubikTestError("demo test failed")

class Paragraph(WrappedText):
    __pre_node_classes__ = []
    __post_node_classes__ = []
    __res__ = {
        'line': re.compile(r"(.*)"),
    }
    def _default_node(self):
        return self

    def parse_match_result(self, line_number, line, match_result):
        self.add_line(line_number, match_result.match.groups()[-1])
        return self._default_node()
    
class Break(WrappedText):
    __pre_node_classes__ = []
    __post_node_classes__ = []
    __res__ = {
        'break': re.compile(r"(<<<BREAK>>>)\s*"),
    }
    def render(self, interactive=False):
        if interactive:
            py23.get_input("Press ENTER to continue...")
            return "=" * 70

    def parse_match_result(self, line_number, line, match_result):
        return self._default_node()

Node.set_default_node_class(Paragraph)
Header.add_post_node_classes(Paragraph, Command, Break)

Paragraph.add_pre_node_classes(Header, Command, Break)
Paragraph.add_post_node_classes(Paragraph, Header, Command)

Command.add_post_node_classes(Result, Command, Break)
Command.set_default_node_class(Result)

Result.add_post_node_classes(Command, Header, Paragraph, Break)


