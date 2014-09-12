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
              'help_environment_variables',
              'HelpEnvironmentVariables',
          ]

from ... import conf

from .functor_help_text import HelpText

def help_environment_variables(test=None, interactive=None, writer=None):
    HelpEnvironmentVariables(test=test, interactive=interactive, writer=writer)()

class HelpEnvironmentVariables(HelpText):
    TEXT = """\
# Environment variables

Currently the only accepted environment variable is '$RUBIK_OPTIONS', that can
be set to a list of valid rubik options. For instance:

$ export RUBIK_OPTIONS='-v --memory-limit 16gb'
$
 
These options will be prepended to the list of command line arguments. So, they
can be overwritten by command line arguments.
"""
