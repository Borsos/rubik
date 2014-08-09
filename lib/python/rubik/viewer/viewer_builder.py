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
    'viewerBuilder',
]

import numpy as np

from ..errors import RubikError
from .viewer_wrapper import ViewerWrapper

def viewerBuilder(logger, viewer_type, data, **viewer_args):
    # to viewer_types:
    if isinstance(viewer_type, (list, tuple)):
        orig_viewer_types = tuple(viewer_type)
    else:
        orig_viewer_types = (viewer_type, )

    # auto-detect viewer_type(s)
    viewer_types = []
    for viewer_type in orig_viewer_types:
        if viewer_type is None or viewer_type == "auto":
            if isinstance(data, np.ndarray):
                if len(data.shape) == 3:
                    # volume
                    viewer_types.extend(("AdvancedVolumeSlicer", "VolumeSlicer"))
                else:
                    raise RubikError("cannot find a valid viewer for {} object with rank {}".format(type(data, len(data.shape))))
            if viewer_type is None:
                raise RubikError("cannot find a valid viewer for {} object".format(type(data)))
        else:
            viewer_types.append(viewer_type)

    # get viewer class:
    viewer_class = None
    for viewer_type in viewer_types:
        if viewer_type == "AdvancedVolumeSlicer":
            try:
                # example from http://docs.enthought.com/mayavi/mayavi/auto/example_volume_slicer_advanced.html#example-volume-slicer-advanced
                from .concrete_advanced_volume_slicer_viewer import ConcreteAdvancedVolumeSlicerViewer
                viewer_class = ConcreteAdvancedVolumeSlicerViewer
                break
            except ImportError as err:
                logger.info("cannot build {!r}: {}: {}".format(viewer_type, type(err).__name__, err))
        elif viewer_type == "VolumeSlicer":
            try:
                # example from http://docs.enthought.com/mayavi/mayavi/auto/example_volume_slicer.html#example-volume-slicer
                from .concrete_volume_slicer_viewer import ConcreteVolumeSlicerViewer
                viewer_class = ConcreteVolumeSlicerViewer
                break
            except ImportError as err:
                logger.info("cannot build {!r}: {}: {}".format(viewer_type, type(err).__name__, err))
        else:
            raise RubikError("unknown viewer_type {!r}".format(viewer_type))
    else:
        raise RubikError("no usable viewer")
    
    # build:
    logger.info("creating {} viewer...".format(viewer_class.__name__))
    return viewer_class(data=data, viewer_args=viewer_args)
