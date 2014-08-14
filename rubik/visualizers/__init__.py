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
    'get_visualizer_class',
    'get_visualizer_types',
    'list_visualizer',
    'list_visualizers',
    'VISUALIZER_TYPES',
]

import sys
import textwrap

from ..errors import RubikError

VISUALIZER_TYPES = ('VolumeSlicer', 'VolumeRender', 'VolumeContour')
_VISUALIZER_CLASSES = {}

def get_visualizer_class(visualizer_type, logger=None):
    if visualizer_type in _VISUALIZER_CLASSES:
        return _VISUALIZER_CLASSES[visualizer_type]
    visualizer_class = None
    try:
        if visualizer_type == "VolumeSlicer":
            # example from http://docs.enthought.com/mayavi/mayavi/auto/example_volume_slicer_advanced.html#example-volume-slicer-advanced
            from .concrete_volume_slicer_visualizer import ConcreteVolumeSlicerVisualizer
            visualizer_class = ConcreteVolumeSlicerVisualizer
        elif visualizer_type == "VolumeRender":
            from .concrete_volume_render_visualizer import ConcreteVolumeRenderVisualizer
            visualizer_class = ConcreteVolumeRenderVisualizer
        elif visualizer_type == "VolumeContour":
            from .concrete_volume_contour_visualizer import ConcreteVolumeContourVisualizer
            visualizer_class = ConcreteVolumeContourVisualizer
        else:
            if logger is not None:
                logger.error("invalid visualizer type {!r}".format(visualizer_type))
    except ImportError as err:
        if logger is not None:
            logger.warning("cannot load {!r}: {}: {}".format(visualizer_type, type(err).__name__, err))
    _VISUALIZER_CLASSES[visualizer_type] = visualizer_class
    return visualizer_class

def get_visualizer_types(self):
    return VISUALIZER_TYPES

def list_visualizers(logger=None, print_function=None):
    for visualizer_type in VISUALIZER_TYPES:
        list_visualizer(visualizer_type, logger=logger, print_function=print_function)

def list_visualizer(visualizer_type, logger=None, print_function=None):
    if print_function is None:
        print_function = lambda message: sys.stdout.write('{}\n'.format(message))
    visualizer_class = get_visualizer_class(visualizer_type, logger)
    if visualizer_class is not None:
        print_function("=== VISUALIZER {}:".format(visualizer_type))
        print_function("    TARGET: {}".format(', '.join('{}D'.format(d) for d in visualizer_class.ConcreteVisualizerClass.DIMENSIONS)))
        print_function("    DESCRIPTION: {}".format(textwrap.fill(visualizer_class.ConcreteVisualizerClass.DESCRIPTION,
                                                                  initial_indent="", subsequent_indent="                 ")))
        for attribute_name, attribute in visualizer_class.ConcreteVisualizerClass.ATTRIBUTES.iteritems():
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
    
