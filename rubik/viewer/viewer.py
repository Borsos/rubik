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
    'VolumeViewer',
]

import numpy as np

from ..errors import RubikError

class Viewer(object):
    ConcreteVolumeClass = None
    def __init__(self, data, viewer_args):
        if not isinstance(data, np.ndarray):
            raise RubikError("cannot create a {} for object of type {}".format(self.__class__.__name__, type(data).__name__))
        elif len(data.shape) != 3:
            raise RubikError("cannot create a {} for {} with shape {}".format(self.__class__.__name__, type(data).__name__, len(data.shape)))
        self.data = data
        self.viewer_args = viewer_args
        self.concrete_viewer = self.ConcreteViewerClass(data=data)
        self.concrete_viewer.set_attributes(**viewer_args)

    def run(self):
        self.concrete_viewer.configure_traits()
        
