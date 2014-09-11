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
    'RUBIK_OPTIONS'
    'RUBIK_DIR'
    'RUBIK_CONFIG'
    'load_rubik_environment'
    'get_rubik_dir'
    'get_rubik_config'
]

import os
import shlex

RUBIK_OPTIONS = None
RUBIK_DIR = None
RUBIK_CONFIG = None

def load_rubik_environment():
    global RUBIK_OPTIONS
    RUBIK_OPTIONS = shlex.split(os.environ.get('RUBIK_OPTIONS', ''))

    global RUBIK_DIR
    global RUBIK_CONFIG
    RUBIK_DIR = os.path.expanduser(os.path.expandvars(os.environ.get('RUBIK_DIR', '~/.rubik')))
    RUBIK_CONFIG = os.path.expanduser(os.path.expandvars(os.environ.get('RUBIK_CONFIG', 'rubik.config')))
    if not os.path.isabs(RUBIK_CONFIG):
        RUBIK_CONFIG = os.path.join(RUBIK_DIR, RUBIK_CONFIG)
    RUBIK_CONFIG = os.path.normpath(os.path.realpath(os.path.abspath(RUBIK_CONFIG)))
    return RUBIK_DIR, RUBIK_CONFIG

load_rubik_environment()

def get_rubik_dir():
    return RUBIK_DIR

def get_rubik_config():
    return RUBIK_CONFIG
