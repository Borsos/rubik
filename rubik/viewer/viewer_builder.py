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
    'viewer_builder',
]

import numpy as np

from .viewers import get_viewer_class
from ..errors import RubikError

def viewer_builder(logger, viewer_type, data, viewer_args):
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
                    viewer_types.extend(("VolumeSlicer", "VolumeRender"))
                else:
                    raise RubikError("cannot find a valid viewer for {} object with rank {}".format(type(data, len(data.shape))))
            if viewer_type is None:
                raise RubikError("cannot find a valid viewer for {} object".format(type(data)))
        else:
            viewer_types.append(viewer_type)

    # get viewer class:
    viewer_class = None
    for viewer_type in viewer_types:
        viewer_class = get_viewer_class(viewer_type, logger)
        if viewer_class is not None:
            break
    else:
        raise RubikError("no usable viewer")
    
    # build:
    logger.info("creating {} viewer...".format(viewer_class.__name__))
    return viewer_class(data=data, viewer_args=viewer_args)
