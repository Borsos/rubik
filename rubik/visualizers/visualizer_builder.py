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
    'visualizer_builder',
]

import numpy as np

from . import get_visualizer_class, VISUALIZER_TYPES
from ..errors import RubikError

def visualizer_builder(logger, visualizer_type, data, visualizer_args):
    # to visualizer_types:
    if isinstance(visualizer_type, (list, tuple)):
        orig_visualizer_types = tuple(visualizer_type)
    else:
        orig_visualizer_types = (visualizer_type, )

    # auto-detect visualizer_type(s)
    visualizer_types = []
    for visualizer_type in orig_visualizer_types:
        if visualizer_type is None or visualizer_type == "auto":
            if isinstance(data, np.ndarray):
                usable_visualizer_type = None
                for vt in VISUALIZER_TYPES:
                    vc = get_visualizer_class(vt, logger)
                    if vc is not None and len(data.shape) in vc.ConcreteVisualizerClass.DIMENSIONS:
                        usable_visualizer_type = vt
                        break
                else:
                    raise RubikError("cannot find a valid visualizer for {} object with rank {}".format(type(data), len(data.shape)))
                if usable_visualizer_type is None:
                    raise RubikError("cannot find a valid visualizer for {} object".format(type(data)))
                visualizer_types.append(usable_visualizer_type)
        else:
            if not visualizer_type in VISUALIZER_TYPES:
                raise RubikError("invalid visualizer_type {!r}".format(visualizer_type))
            visualizer_types.append(visualizer_type)

    # get visualizer class:
    visualizer_class = None
    for visualizer_type in visualizer_types:
        visualizer_class = get_visualizer_class(visualizer_type, logger)
        if visualizer_class is not None:
            break
    else:
        raise RubikError("no usable visualizer")
    
    # build:
    logger.info("creating {} visualizer...".format(visualizer_class.__name__))
    return visualizer_class(logger=logger, data=data, visualizer_args=visualizer_args)
