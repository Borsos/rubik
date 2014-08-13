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
    'VolumeRender',
]

import numpy as np

from traits.api import HasTraits, Instance, Array, \
    Range, Float, on_trait_change
from traitsui.api import View, Item, HGroup, Group, \
    RangeEditor

from tvtk.api import tvtk
from tvtk.pyface.scene import Scene

from mayavi import mlab
from mayavi.core.api import PipelineBase, Source
from mayavi.core.ui.api import SceneEditor, MayaviScene, \
                                MlabSceneModel

################################################################################
# The object implementing the dialog
class VolumeRender(HasTraits):
    # The data to plot
    data = Array()

    # The 4 views displayed
    scene3d = Instance(MlabSceneModel, ())

    # The data source
    data_src3d = Instance(Source)

    _axis_names = dict(x=0, y=1, z=2)

    data_min = Float()
    data_max = Float()
    vmin = Float()
    vmax = Float()
    vmin_range = Range('data_min', 'data_max', 'vmin')
    vmax_range = Range('data_min', 'data_max', 'vmax')

    #---------------------------------------------------------------------------
    def __init__(self, **traits):
        super(VolumeRender, self).__init__(**traits)
        self.data_min, self.data_max = np.min(self.data), np.max(self.data)

    def set_attributes(self, **attributes):
        for attribute_name, attribute_value in attributes.items():
            setattr(self, attribute_name, attribute_value)

    def _vmin_default(self):
        return np.min(self.data)

    def _vmax_default(self):
        return np.max(self.data)

    @on_trait_change('vmin')
    def change_vmin(self):
        if self.vmin > self.vmax:
            self.vmax = self.vmin
        
    @on_trait_change('vmax')
    def change_vmax(self):
        if self.vmax < self.vmin:
            self.vmin = self.vmax
        

    #---------------------------------------------------------------------------
    # Default values
    #---------------------------------------------------------------------------
    def _data_src3d_default(self):
        return mlab.pipeline.scalar_field(self.data,
                            figure=self.scene3d.mayavi_scene)

    def make_ipw_3d(self, axis_name):
        ipw = mlab.pipeline.image_plane_widget(self.data_src3d,
                        figure=self.scene3d.mayavi_scene,
                        plane_orientation='%s_axes' % axis_name)
        return ipw

#    def _ipw_3d_x_default(self):
#        return self.make_ipw_3d('x')
#
#    def _ipw_3d_y_default(self):
#        return self.make_ipw_3d('y')
#
#    def _ipw_3d_z_default(self):
#        return self.make_ipw_3d('z')


    #---------------------------------------------------------------------------
    # Scene activation callbaks
    #---------------------------------------------------------------------------
    @on_trait_change('scene3d.activated,vmin,vmax')
    def display_scene3d(self):
        outline = mlab.pipeline.volume(self.data_src3d,
            figure=self.scene3d.mayavi_scene,
            vmin=self.vmin,
            vmax=self.vmax,
        )
        self.scene3d.mlab.view(40, 50)

        self.scene3d.scene.background = (0, 0, 0)
        # Keep the view always pointing up
        self.scene3d.scene.interactor.interactor_style = \
                                 tvtk.InteractorStyleTerrain()


    #---------------------------------------------------------------------------
    # The layout of the dialog created
    #---------------------------------------------------------------------------
    view = View(
        HGroup(
            Group(
                Item('scene3d',
                    editor=SceneEditor(scene_class=MayaviScene),
                    height=500, width=600),
                show_labels=False,
            ),
            Group(
                Item('vmin',
                    editor=RangeEditor(
                        low_name='data_min',
                        high_name='data_max',
                        format="%.1f",
                        label_width=10,
                        mode="slider",
                    ),
                ),
                Item('vmax',
                    editor=RangeEditor(
                        low_name='data_min',
                        high_name='data_max',
                        format="%.1f",
                        label_width=10,
                        mode="slider",
                    ),
                ),
            ),
        ),
        resizable=True,
        title='Volume Render',
    )


if __name__ == "__main__":
    ################################################################################
    # Create some data
    x, y, z = np.ogrid[-5:5:64j, -5:5:64j, -5:5:64j]
    data = np.sin(3*x)/x + 0.05*z**2 + np.cos(3*y)

    m = VolumeRender(data=data)
    m.configure_traits()
