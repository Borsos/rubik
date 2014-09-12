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
              'help_user_defined_variables',
              'HelpUserDefinedVariables',
          ]

from .functor_help_example import HelpExample

def help_user_defined_variables(test=None, interactive=None, writer=None):
    HelpUserDefinedVariables(test=test, interactive=interactive, writer=writer)()

class HelpUserDefinedVariables(HelpExample):
    TEXT = """\
# User defined variables

It is possible to use expressions to set variables; this variables can then
be used in the following expressions. For instance:

$ rubik -e 'x = cb.linear_cube("3x3", start=0)' \\
        -e 'y = cb.linear_cube("3x3", start=1)' \\
        -e alpha=1.5 \\
        -e beta=-0.5 \\
        -e 'alpha * x + beta * y' \\
        --print
[[-0.5  0.5  1.5]
 [ 2.5  3.5  4.5]
 [ 5.5  6.5  7.5]]
$

"""
