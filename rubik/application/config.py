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
from ..units import Memory
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
    OUTPUT_ACTION_NONE = 'none'
    OUTPUT_ACTIONS = [OUTPUT_ACTION_VISUALIZE, OUTPUT_ACTION_PRINT, OUTPUT_ACTION_STATS, OUTPUT_ACTION_HISTOGRAM, OUTPUT_ACTION_NONE]
    if py23.PY3:
        DEFAULT_OUTPUT_ACTION = OUTPUT_ACTION_NONE
    else:
        DEFAULT_OUTPUT_ACTION = OUTPUT_ACTION_VISUALIZE
    
    VISUALIZER_VOLUME_SLICER = 'VolumeSlicer'
    VISUALIZER_VOLUME_RENDER = 'VolumeRender'
    VISUALIZER_VOLUME_CONTOUR = 'VolumeContour'
    VISUALIZERS = [VISUALIZER_VOLUME_SLICER, VISUALIZER_VOLUME_RENDER, VISUALIZER_VOLUME_CONTOUR]
    DEFAULT_VISUALIZER = VISUALIZERS[0]

    CONFIG_DEFAULTS = OrderedDict((
        ('preferred_output_action',	'visualize'),
        ('preferred_visualizer',        'VolumeSlicer'),
        ('default_options',             ''),
        ('default_data_type',           conf.DEFAULT_DATA_TYPE),
        ('default_clobber',             str(conf.DEFAULT_CLOBBER)),
        ('default_read_mode',           conf.DEFAULT_READ_MODE),
        ('default_memory_limit',        str(conf.DEFAULT_MEMORY_LIMIT)),
        ('default_optimized_min_size',  str(conf.DEFAULT_OPTIMIZED_MIN_SIZE)),
        ('default_file_format',         str(conf.DEFAULT_FILE_FORMAT)),
        ('default_warnings',            ''),
        ('default_report_level',        '0'),
        ('default_verbose_level',       '1'),
        ('default_trace_errors',        'False'),
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
            self.default_options = shlex.split(config.get("general", "default_options"))
            self.default_data_type = config.get("general", "default_data_type")
            self.default_file_format = config.get("general", "default_file_format")
            self.default_memory_limit = Memory(config.get("general", "default_memory_limit"))
            self.default_read_mode = config.get("general", "default_read_mode")
            self.default_optimized_min_size = Memory(config.get("general", "default_optimized_min_size"))
            self.default_clobber = config.getboolean("general", "default_clobber")
            self.default_warnings = shlex.split(config.get("general", "default_warnings"))
            self.default_trace_errors = config.getboolean("general", "default_trace_errors")
            self.default_verbose_level = config.getint("general", "default_verbose_level")
            self.default_report_level = config.getint("general", "default_report_level")
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
        
    def get_default_options(self):
        return self._default_options
    def set_default_options(self, a):
        self._default_options = a
    default_options = property(get_default_options, set_default_options)

    def get_default_warnings(self):
        return self._default_warnings
    def set_default_warnings(self, wl):
        warnings = []
        for w in wl:
            if not w in conf.ALL_WARNINGS:
                raise RubikError("invalid warning {}".format(w))
            warnings.append(w)
        self._default_warnings = warnings
    default_warnings = property(get_default_warnings, set_default_warnings)

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

    def get_default_data_type(self):
        return self._default_data_type
    def set_default_data_type(self, t):
        if not t in conf.DATA_TYPES:
            raise RubikError("invalid data type {}".format(t))
        self._default_data_type = t
    default_data_type = property(get_default_data_type, set_default_data_type)

    def get_default_read_mode(self):
        return self._default_read_mode
    def set_default_read_mode(self, t):
        if not t in conf.READ_MODES:
            raise RubikError("invalid read mode {}".format(t))
        self._default_read_mode = t
    default_read_mode = property(get_default_read_mode, set_default_read_mode)

    def get_default_file_format(self):
        return self._default_file_format
    def set_default_file_format(self, t):
        if not t in conf.FILE_FORMATS:
            raise RubikError("invalid file format {}".format(t))
        self._default_file_format = t
    default_file_format = property(get_default_file_format, set_default_file_format)

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
