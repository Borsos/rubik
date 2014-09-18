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
from .  import environment
from ..units import Memory
from ..errors import RubikError
from ..cubes.dtypes import DEFAULT_DATA_TYPE

if py23.PY3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser



class Config(object):
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
    
    VISUALIZER_VolumeSlicer = 'VolumeSlicerViewer'
    VISUALIZERS = [VISUALIZER_VolumeSlicer]
    DEFAULT_VISUALIZER = VISUALIZERS[0]

    CONTROLLER_Controller = 'Controller'
    CONTROLLERS = [CONTROLLER_Controller]
    DEFAULT_CONTROLLER = CONTROLLERS[0]

    CONFIG_DEFAULTS = OrderedDict((
        ('preferred_output_action',	'visualize'),
        ('preferred_controller',        'Controller'),
        ('preferred_visualizer',        DEFAULT_VISUALIZER),
        ('default_options',             ''),
        ('default_data_type',           DEFAULT_DATA_TYPE),
        ('default_clobber',             str(conf.DEFAULT_CLOBBER)),
        ('default_memory_limit',        str(conf.DEFAULT_MEMORY_LIMIT)),
        ('default_read_threshold_size', str(conf.DEFAULT_READ_THRESHOLD_SIZE)),
        ('default_file_format',         str(conf.DEFAULT_FILE_FORMAT)),
        ('default_warnings',            ''),
        ('default_report_level',        '1'),
        ('default_verbose_level',       '1'),
        ('default_trace_errors',        'False'),
    ))

    CURRENT_CONFIG_FILENAME = None
    CURRENT_CONFIG= None
    def __init__(self, rubik_config=None, rubik_dir=None):
        rubik_dir, rubik_config = self.get_config_rubik_dir_and_config(rubik_config=rubik_config, rubik_dir=rubik_dir)
        self.rubik_dir = rubik_dir
        self.rubik_config = rubik_config
        self.create_missing_files()
        config = ConfigParser(defaults=self.CONFIG_DEFAULTS)
        if os.path.exists(self.rubik_config):
            try:
                config.read(self.rubik_config)
            except Exception as err:
                raise RubikError("cannot read config file {}: {}: {}".format(self.rubik_config, type(err).__name__, err))
        if not config.has_section("general"):
            config.add_section("general")
        try:
            self.preferred_output_action = config.get("general", "preferred_output_action")
            self.preferred_controller = config.get("general", "preferred_controller")
            self.preferred_visualizer = config.get("general", "preferred_visualizer")
            self.default_options = shlex.split(config.get("general", "default_options"))
            self.default_data_type = config.get("general", "default_data_type")
            self.default_file_format = config.get("general", "default_file_format")
            self.default_memory_limit = Memory(config.get("general", "default_memory_limit"))
            self.default_read_threshold_size = Memory(config.get("general", "default_read_threshold_size"))
            self.default_clobber = config.getboolean("general", "default_clobber")
            self.default_warnings = shlex.split(config.get("general", "default_warnings"))
            self.default_trace_errors = config.getboolean("general", "default_trace_errors")
            self.default_verbose_level = config.getint("general", "default_verbose_level")
            self.default_report_level = config.getint("general", "default_report_level")
        except Exception as err:
            raise RubikError("invalid config file {}: {}: {}".format(self.rubik_config, type(err).__name__, err))
        self.visualizer_attributes = {
            self.VISUALIZER_VolumeSlicer: self.read_attribute_file(self.get_visualizer_defaults_filename(self.VISUALIZER_VolumeSlicer)),
        }
        self.controller_attributes = {
            self.CONTROLLER_Controller: self.read_attribute_file(self.get_controller_defaults_filename(self.CONTROLLER_Controller)),
        }

    @classmethod
    def get_config_rubik_dir_and_config(cls, rubik_config=None, rubik_dir=None):
        RUBIK_DIR = environment.get_rubik_dir()
        RUBIK_CONFIG = environment.get_rubik_config()
        if rubik_dir is None:
            rubik_dir = RUBIK_DIR
        else:
            rubik_dir = os.path.expanduser(os.path.expandvars(rubik_dir))
        if rubik_config is None:
            rubik_config = RUBIK_CONFIG
        else:
            rubik_config = os.path.expanduser(os.path.expandvars(rubik_config))
        if not os.path.isabs(rubik_config):
            rubik_config = os.path.join(rubik_dir, rubik_config)
        rubik_config = os.path.normpath(os.path.realpath(os.path.abspath(rubik_config)))
        return rubik_dir, rubik_config

    def get_option(self, key):
        value = getattr(self, key)
        if isinstance(value, (tuple, list)):
            return ' '.join(repr(o) for o in value)
        elif isinstance(value, py23.BASE_STRING):
            return value
        else:
            return str(value)

    @classmethod
    def get_config(cls, rubik_config=None, rubik_dir=None):
        rubik_dir, rubik_config = cls.get_config_rubik_dir_and_config(rubik_config=rubik_config, rubik_dir=rubik_dir)
        if cls.CURRENT_CONFIG is None or cls.CURRENT_CONFIG_FILENAME != rubik_config:
            cls.CURRENT_CONFIG_FILENAME = rubik_config
            cls.CURRENT_CONFIG = cls(rubik_config=rubik_config, rubik_dir=rubik_dir)
        return cls.CURRENT_CONFIG
        
    @classmethod
    def get_defaults_filename(cls, type, name):
        return os.path.join(environment.get_rubik_dir(), '{}-{}.defaults'.format(type, name))

    @classmethod
    def get_visualizer_defaults_filename(cls, name):
        return cls.get_defaults_filename("VISUALIZER", name)

    @classmethod
    def get_controller_defaults_filename(cls, name):
        return cls.get_defaults_filename("CONTROLLER", name)

    def create_missing_files(self):
        if not os.path.exists(self.rubik_dir):
            os.makedirs(self.rubik_dir)
        if not os.path.exists(self.rubik_config):
            with open(self.rubik_config, 'w') as f_out:
                f_out.write("# configuration file for rubik {}\n".format(conf.VERSION))
                f_out.write("[general]\n")
                for key, value in self.CONFIG_DEFAULTS.items():
                    f_out.write("# {} = {}\n".format(key, value))
        for visualizer, filename in (
                                     (self.VISUALIZER_VolumeSlicer, self.get_visualizer_defaults_filename(self.VISUALIZER_VolumeSlicer)),
                                     (self.CONTROLLER_Controller, self.get_controller_defaults_filename(self.CONTROLLER_Controller)),
                                    ):
            if not os.path.exists(filename):
                with open(filename, 'w') as f_out:
                    f_out.write("# Rubik {}\n".format(conf.VERSION))
                    f_out.write("# This file contains the default attributes for the {} visualizer\n".format(visualizer))
                    f_out.write("# e.g.:\n")
                    f_out.write("# colorbar = True\n")

    def write_config_file(self, file):
        if isinstance(file, py23.BASE_STRING):
            with open(file, "w") as f_out:
                self.write_config_file(f_out)
        else:
            file.write("# configuration file for rubik {}\n".format(conf.VERSION))
            file.write("[general]\n")
            for key, default_value in self.CONFIG_DEFAULTS.items():
                value = self.get_option(key)
                if value == default_value:
                    comment = "# "
                else:
                    comment = ""
                file.write("{}{} = {}\n".format(comment, key, value))
        
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

def get_config(rubik_config=None, rubik_dir=None):
    return Config.get_config(rubik_config=rubik_config, rubik_dir=rubik_dir)
