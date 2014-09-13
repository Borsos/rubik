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
    'get_controller_class',
    'get_controller_types',
    'get_visualizer_class',
    'get_visualizer_types',
    'list_controller',
    'list_controllers',
    'list_visualizer',
    'list_visualizers',
]

import textwrap

from ..errors import RubikError
from ..application.log import get_print

_VISUALIZER_TYPES = ('VolumeSlicer', )
_VISUALIZER_CLASSES = {}

_CONTROLLER_TYPES = ('Controller', )
_CONTROLLER_CLASSES = {}

def get_visualizer_class(visualizer_type, logger=None):
    if visualizer_type in _VISUALIZER_CLASSES:
        return _VISUALIZER_CLASSES[visualizer_type]
    visualizer_class = None
    try:
        if visualizer_type == "VolumeSlicer":
            from .impl.volume_slicer import VolumeSlicer
            visualizer_class = VolumeSlicer
        else:
            if logger is not None:
                logger.error("invalid visualizer type {!r}".format(visualizer_type))
    except ImportError as err:
        if logger is not None:
            logger.warning("cannot load {!r}: {}: {}".format(visualizer_type, type(err).__name__, err))
    _VISUALIZER_CLASSES[visualizer_type] = visualizer_class
    return visualizer_class

def get_controller_class(controller_type, logger=None):
    if controller_type in _CONTROLLER_CLASSES:
        return _CONTROLLER_CLASSES[controller_type]
    controller_class = None
    try:
        if controller_type == "Controller":
            from .impl.controller import Controller
            controller_class = Controller
        else:
            if logger is not None:
                logger.error("invalid controller type {!r}".format(controller_type))
    except ImportError as err:
        if logger is not None:
            logger.warning("cannot load {!r}: {}: {}".format(controller_type, type(err).__name__, err))
    _CONTROLLER_CLASSES[controller_type] = controller_class
    return controller_class

def get_visualizer_types():
    return _VISUALIZER_TYPES

def get_controller_types():
    return _CONTROLLER_TYPES

def list_controllers(logger=None, print_function=None):
    for controller_type in _CONTROLLER_TYPES:
        list_controller(controller_type, logger=logger, print_function=print_function)

def list_controller(controller_type, logger=None, print_function=None):
    if print_function is None:
        print_function = get_print() 
    controller_class = get_controller_class(controller_type, logger)
    if controller_class is not None:
        print_function("=== CONTROLLER {}:".format(controller_type))
        print_function("    TARGET DIMENSIONS: {}".format(controller_class.DIMENSIONS))
        print_function("    DESCRIPTION: {}".format(textwrap.fill(controller_class.DESCRIPTION,
                                                                  initial_indent="", subsequent_indent="                 ")))
        for attribute_name, attribute in controller_class.ATTRIBUTES.iteritems():
            print_function("    * ATTRIBUTE {}:".format(attribute_name))
            print_function("      TYPE: {}".format(textwrap.fill(str(attribute.attribute_type()),
                                                          initial_indent="",
                                                          subsequent_indent="          ",
                                                          break_on_hyphens=False)))
            print_function("      DEFAULT: {!r}".format(attribute.default()))
            print_function("      DESCRIPTION: {}".format(textwrap.fill(attribute.description(),
                                                          initial_indent="",
                                                          subsequent_indent="          ",
                                                          break_on_hyphens=False)))
def list_visualizers(logger=None, print_function=None):
    for visualizer_type in _VISUALIZER_TYPES:
        list_visualizer(visualizer_type, logger=logger, print_function=print_function)

def list_visualizer(visualizer_type, logger=None, print_function=None):
    if print_function is None:
        print_function = get_print()
    visualizer_class = get_visualizer_class(visualizer_type, logger)
    if visualizer_class is not None:
        print_function("=== VISUALIZER {}:".format(visualizer_type))
        print_function("    TARGET DIMENSIONS: {}".format(visualizer_class.DIMENSIONS))
        print_function("    DESCRIPTION: {}".format(textwrap.fill(visualizer_class.DESCRIPTION,
                                                                  initial_indent="", subsequent_indent="                 ")))
        for attribute_name, attribute in visualizer_class.ATTRIBUTES.iteritems():
            print_function("    * ATTRIBUTE {}:".format(attribute_name))
            print_function("      TYPE: {}".format(textwrap.fill(str(attribute.attribute_type()),
                                                          initial_indent="",
                                                          subsequent_indent="          ",
                                                          break_on_hyphens=False)))
            print_function("      DEFAULT: {!r}".format(attribute.default()))
            print_function("      DESCRIPTION: {}".format(textwrap.fill(attribute.description(),
                                                          initial_indent="",
                                                          subsequent_indent="          ",
                                                          break_on_hyphens=False)))
    
