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
    'Config'
    'get_config'
]

import os
import shlex
from collections import OrderedDict

from .. import py23
from .. import conf
from .  import log
from ..errors import RubikError

if py23.PY3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser



class Config(object):
    RUBIK_DIR = os.path.expanduser("~/.rubik")
    CONFIG_FILE = os.path.join(RUBIK_DIR, 'rubik.config')
    VOLUME_SLICER_FILE = os.path.join(RUBIK_DIR, 'VolumeSlicer.defaults')
    VOLUME_RENDER_FILE = os.path.join(RUBIK_DIR, 'VolumeRender.defaults')
    VOLUME_CONTOUR_FILE = os.path.join(RUBIK_DIR, 'VolumeContour.defaults')

    OUTPUT_ACTION_VISUALIZE = 'visualize'
    OUTPUT_ACTION_PRINT = 'print'
    OUTPUT_ACTION_STATS = 'stats'
    OUTPUT_ACTION_HISTOGRAM = 'histogram'
    OUTPUT_ACTIONS = [OUTPUT_ACTION_VISUALIZE, OUTPUT_ACTION_PRINT, OUTPUT_ACTION_STATS, OUTPUT_ACTION_HISTOGRAM]
    DEFAULT_OUTPUT_ACTION = OUTPUT_ACTIONS[0]
    
    VISUALIZER_VOLUME_SLICER = 'VolumeSlicer'
    VISUALIZER_VOLUME_RENDER = 'VolumeRender'
    VISUALIZER_VOLUME_CONTOUR = 'VolumeContour'
    VISUALIZERS = [VISUALIZER_VOLUME_SLICER, VISUALIZER_VOLUME_RENDER, VISUALIZER_VOLUME_CONTOUR]
    DEFAULT_VISUALIZER = VISUALIZERS[0]

    CONFIG_DEFAULTS = OrderedDict((
        ('preferred_output_action',	'visualize'),
        ('preferred_visualizer',        'VolumeSlicer'),
    ))
    def __init__(self, filename=None):
        self.create_missing_files()
        config = ConfigParser(defaults=self.CONFIG_DEFAULTS)
        if os.path.exists(self.CONFIG_FILE):
            try:
                config.read(self.CONFIG_FILE)
            except Exception as err:
                raise RubikError("cannot read config file {}: {}: {}".format(self.CONFIG_FILE, type(err).__name__, err))
        if not config.has_section("general"):
            config.add_section("general")
        try:
            self.preferred_output_action = config.get("general", "preferred_output_action")
            self.preferred_visualizer = config.get("general", "preferred_visualizer")
        except Exception as err:
            raise RubikError("invalid config file {}: {}: {}".format(self.CONFIG_FILE, type(err).__name__, err))
        self.visualizer_attributes = {
            'VolumeSlicer': self.read_attribute_file(self.VOLUME_SLICER_FILE),
            'VolumeRender': self.read_attribute_file(self.VOLUME_RENDER_FILE),
            'VolumeContour': self.read_attribute_file(self.VOLUME_CONTOUR_FILE),
        }

    def create_missing_files(self):
        if not os.path.exists(self.RUBIK_DIR):
            os.makedirs(self.RUBIK_DIR)
        if not os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'w') as f_out:
               f_out.write("# configuration file for rubik {}\n".format(conf.VERSION))
               f_out.write("[general]\n")
               for key, value in self.CONFIG_DEFAULTS.iteritems():
                   f_out.write("# {} = {}\n".format(key, value))
        for visualizer, filename in (('VolumeSlicer', self.VOLUME_SLICER_FILE),
                                     ('VolumeRender', self.VOLUME_RENDER_FILE),
                                     ('VolumeContour', self.VOLUME_CONTOUR_FILE)):
            if not os.path.exists(filename):
                with open(filename, 'w') as f_out:
                    f_out.write("# Rubik {}\n".format(conf.VERSION))
                    f_out.write("# This file contains the default attributes for the {} visualizer\n".format(visualizer))
                    f_out.write("# e.g.:\n")
                    f_out.write("# colorbar = True\n")
        
    def get_preferred_output_action(self):
        return self._preferred_output_action
    def set_preferred_output_action(self, a):
        if not a in self.OUTPUT_ACTIONS:
            raise RubikError("invalid output action {}".format(a))
        self._preferred_output_action = a
    preferred_output_action = property(get_preferred_output_action, set_preferred_output_action)

    def get_preferred_visualizer(self):
        return self._preferred_visualizer
    def set_preferred_visualizer(self, v):
        if not v in self.VISUALIZERS:
            raise RubikError("invalid visualizer {}".format(v))
        self._preferred_visualizer = v
    preferred_visualizer = property(get_preferred_visualizer, set_preferred_visualizer)

    @classmethod
    def read_attribute_file(cls, filename):
        logger = log.get_logger()
        attributes = {}
        if not os.path.exists(filename):
            logger.warn("warning: attributes file {} does not exists".format(filename))
        else:
            try:
                with open(filename, "r") as f_in:
                    lines = f_in.readlines()
            except Exception as err:
                raise RubikError("cannot read attributes file {}: {}: {}".format(filename, type(err).__name__, err))
            for line_no, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith('#'):
                    # a comment
                    continue
                kv = line.split('=', 2)
                if len(kv) != 2:
                    raise RubikError("attributes file {}, line #{}: {!r}: invalid line".format(filename, line_no, line))
                key = kv[0].strip()
                vals = shlex.split(kv[1].strip())
                if len(vals) != 1:
                    raise RubikError("attributes file {}, line #{}: {!r}: invalid value {!r}".format(filename, line_no, line, kv[1].strip()))
                attributes[key] = vals[0]
        return attributes

CONFIG = None

def get_config():
    global CONFIG
    if CONFIG is None:
        CONFIG = Config()
    return CONFIG
