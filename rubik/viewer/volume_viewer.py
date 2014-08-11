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
from .viewer_wrapper import ViewerWrapper

class VolumeViewer(ViewerWrapper):
    ConcreteVolumeClass = None
    def __init__(self, data, **viewer_args):
        if not isinstance(data, np.ndarray):
            raise RubikError("cannot create a {} for object of type {}".format(self.__class__.__name__, type(data).__name__))
        elif len(data.shape) != 3:
            raise RubikError("cannot create a {} for {} with shape {}".format(self.__class__.__name__, type(data).__name__, len(data.shape)))
        super(VolumeViewer, self).__init__(data=data, viewer_args=viewer_args)
        self.volume_viewer = self.ConcreteVolumeClass(data=data)

    def run(self):
        self.volume_viewer.configure_traits()
        
