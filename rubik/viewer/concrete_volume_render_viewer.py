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
    'ConcreteVolumeRenderViewer',
]

from .volume_viewer import VolumeViewer

# from http://docs.enthought.com/mayavi/mayavi/auto/example_volume_slicer_advanced.html#example-volume-slicer-advanced
from .impl.volume_render import VolumeRender

try:
    # disable vtk warnings
    import vtk 
    vtk.vtkObject.GlobalWarningDisplayOff()
except:
    import traceback
    traceback.print_exc()
    pass

class ConcreteVolumeRenderViewer(VolumeViewer):
    ConcreteVolumeClass = VolumeRender
        
