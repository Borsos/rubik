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

from . import get_visualizer_class, get_visualizer_types
from ..errors import RubikError
from ..application.config import get_config

def visualizer_builder(logger, controller, visualizer_type, data, attributes=None, attribute_files=None):
    # defaults:
    if attributes is None:
        attributes = {}
    if attribute_files is None:
        attribute_files = []

    # config instance:
    config = get_config()

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
                usable_visualizer_types = []
                for vt in get_visualizer_types():
                    vc = get_visualizer_class(vt, logger)
                    if vc is not None and vc.DATA_CHECK(data):
                        usable_visualizer_types.append(vt)
                if not usable_visualizer_types:
                    raise RubikError("cannot find a valid visualizer for {} object with rank {}".format(type(data), len(data.shape)))
                if config.preferred_visualizer in usable_visualizer_types:
                    usable_visualizer_type = config.preferred_visualizer
                else:
                    usable_visualizer_type = usable_visualizer_types[0]
                if usable_visualizer_type is None:
                    raise RubikError("cannot find a valid visualizer for {} object".format(type(data)))
                visualizer_types.append(usable_visualizer_type)
        else:
            if not visualizer_type in get_visualizer_types():
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
    
    # attributes:
    visualizer_attributes = {}
    visualizer_attributes.update(config.visualizer_attributes.get(visualizer_type, {}))
    for attribute_file in attribute_files:
        visualizer_attributes.update(config.read_attribute_file(attribute_file))
    visualizer_attributes.update(dict(attributes))

    # build:
    logger.info("creating {} visualizer...".format(visualizer_class.__name__))
    visualizer = controller.add_view(visualizer_class, data=data) ###, attributes=visualizer_attributes)
    return visualizer
