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
              'help_configuration',
              'HelpConfiguration',
          ]

from .functor_help_text import HelpText
from ..config import Config
from ...table import Table

def help_configuration(test=None, interactive=None, writer=None):
    HelpConfiguration(test=test, interactive=interactive, writer=writer)()

class HelpConfiguration(HelpText):
    TEXT = None
    def get_text(self):
        text = """\
# Configuration

Rubik can be configured. A configuration file ($RUBIK_CONFIG) contained in a
configuration dir ($RUBIK_DIR) are used to configure rubik
(see --help-environment-variables/-hE option).

The configuration file can be used to set default values for some options:

"""
        table = Table(headers=['KEY', '', 'DEFAULT_VALUE'])
        for key, default_value in Config.CONFIG_DEFAULTS.items():
            table.add_row((key, "=", repr(default_value)))

        text += table.render() + '\n'
        return text
