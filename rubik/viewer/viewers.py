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
    'get_viewer_class',
    'list_viewer',
    'list_viewers',
    'VIEWER_TYPES',
]

import textwrap

from ..errors import RubikError

VIEWER_TYPES = ('VolumeSlicer', 'VolumeRender', 'VolumeContour')
_VIEWER_CLASSES = {}

def get_viewer_class(viewer_type, logger=None):
    if viewer_type in _VIEWER_CLASSES:
        return _VIEWER_CLASSES[viewer_type]
    viewer_class = None
    try:
        if viewer_type == "VolumeSlicer":
            # example from http://docs.enthought.com/mayavi/mayavi/auto/example_volume_slicer_advanced.html#example-volume-slicer-advanced
            from .concrete_volume_slicer_viewer import ConcreteVolumeSlicerViewer
            viewer_class = ConcreteVolumeSlicerViewer
        elif viewer_type == "VolumeRender":
            from .concrete_volume_render_viewer import ConcreteVolumeRenderViewer
            viewer_class = ConcreteVolumeRenderViewer
        elif viewer_type == "VolumeContour":
            from .concrete_volume_contour_viewer import ConcreteVolumeContourViewer
            viewer_class = ConcreteVolumeContourViewer
        else:
            if logger is not None:
                logger.error("invalid viewer type {!r}".format(viewer_type))
    except ImportError as err:
        if logger is not None:
            logger.warning("cannot load {!r}: {}: {}".format(viewer_type, type(err).__name__, err))
    _VIEWER_CLASSES[viewer_type] = viewer_class
    return viewer_class

def list_viewers(logger):
    for viewer_type in VIEWER_TYPES:
        list_viewer(viewer_type, logger)

def list_viewer(viewer_type, logger):
    viewer_class = get_viewer_class(viewer_type, logger)
    if viewer_class is not None:
        print "===", viewer_type
        for attribute_name, attribute in viewer_class.ConcreteViewerClass.ATTRIBUTES.iteritems():
            print "   * {}:".format(attribute_name)
            print "     default: {!r}".format(attribute.default())
            print "     usable for: {}".format(', '.join('{}D'.format(d) for d in viewer_class.ConcreteViewerClass.DIMENSIONS))
            print textwrap.fill(attribute.description(), initial_indent="     ", subsequent_indent="       ", break_on_hyphens=False)
    
