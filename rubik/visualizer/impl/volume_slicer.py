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
    'VolumeSlicer',
]

import numpy as np
import collections

from traits.api import HasTraits, Instance, Array, \
    Int, Str, Float, Bool, Enum, \
    Button, Range, \
    on_trait_change

from traitsui.api import View, \
    Item, \
    Action, \
    HGroup, \
    Group, \
    HSplit, \
    EnumEditor, \
    RangeEditor, \
    ButtonEditor

from traitsui.handler import Handler, ModelView

from tvtk.api import tvtk
from tvtk.pyface.scene import Scene

from mayavi import mlab
from mayavi.core.api import PipelineBase, Source
from mayavi.core.ui.api import SceneEditor, MayaviScene, \
                                MlabSceneModel

from .base_visualizer_impl import BaseVisualizerImpl
from .attributes import \
    LocateModeAttribute, \
    LocateValueAttribute

from .attributes import \
    LOCATE_MODE_MIN, \
    LOCATE_MODE_MAX, \
    LOCATE_MODE_VALUE, \
    LOCATE_MODES

class VolumeSlicerHandler(ModelView):
    def init(self, info):
        info.ui.title = VolumeSlicer.default_window_title()
        info.object.add_handler(self)

    def _on_close(self, info):
        info.ui.dispose()


class VolumeSlicer(HasTraits, BaseVisualizerImpl):
    ATTRIBUTES = collections.OrderedDict((
        ('locate_mode', LocateModeAttribute()),
        ('locate_value', LocateValueAttribute()),
    ))
    DIMENSIONS = "2D, 3D, 4D"
    DATA_CHECK = classmethod(lambda cls, data: 2 <= len(data.shape) <= 4)
    DESCRIPTION = """\
Volume slicer visualizer
"""

    # window_title
    window_title = Str()

    # The data to plot
    data = Array()

    # The 4 views displayed
    scene3d = Instance(MlabSceneModel, ())
    scene_x = Instance(MlabSceneModel, ())
    scene_y = Instance(MlabSceneModel, ())
    scene_z = Instance(MlabSceneModel, ())

    # The data source
    data_src3d = Instance(Source)

    # The image plane widgets of the 3D scene
    ipw_3d_x = Instance(PipelineBase)
    ipw_3d_y = Instance(PipelineBase)
    ipw_3d_z = Instance(PipelineBase)

    x_index = Int()
    y_index = Int()
    z_index = Int()

    clip_min = Float()
    clip_max = Float()

    data_value = Str()

    locate_mode = Enum(*LOCATE_MODES)
    locate_low = Float()
    locate_high = Float()
    locate_value = Range(low='locate_low', high='locate_high')
    locate_mode_is_value = Bool()
    locate_prev_button = Button()
    locate_nearest_button = Button()
    locate_next_button = Button()
    
    done = Bool(False)

    LABEL_WIDTH = 20
    SCENE_WIDTH = 200
    SCENE_HEIGHT = 200
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 650

    def __init__(self, controller, **traits):
        HasTraits.__init__(self, **traits)
        BaseVisualizerImpl.__init__(self, controller=controller)
        # set window_title
        self.window_title = self.name
        # Force the creation of the image_plane_widgets:
        self.ipw_3d_x
        self.ipw_3d_y
        self.ipw_3d_z

    @classmethod
    def get_geometry(cls, geometry):
        if isinstance(geometry, str):
            try:
                ws, hs = geometry.split('x', 2)
                return int(ws), int(hs)
            except Exception as err:
                raise ValueError("invalid geometry {}: {}: {}".format(geometry, type(err).__name__, err))
        elif isinstance(geometry, (list, tuple)) and len(geometry) == 2:
            return geometry
        else:
            raise ValueError("invalid geometry {}".format(geometry))

    @classmethod
    def set_window_geometry(cls, geometry):
        width, height = self.get_geometry(geometry)
        cls.WINDOW_WIDTH = width
        cls.WINDOW_HEIGHT = height

    @classmethod
    def set_scene_geometry(cls, geometry):
        width, height = self.get_geometry(geometry)
        cls.SCENE_WIDTH = width
        cls.SCENE_HEIGHT = height

    ### U t i l i t i e s :
    def get_value(self):
        data = self.data_src3d.scalar_data
        if len(data.shape) == 2:
            return data[self.x_index, self.y_index]
        else:
            return data[self.x_index, self.y_index, self.z_index]

    def get_data_value(self):
        return str(self.get_value())

    def update_data_value(self):
        self.data_value = self.get_data_value()

    def set_volume(self, data):
        self.data = data
        self.data_src3d.scalar_data = data
        self.set_locate_range()

    def update_clip_range(self, clip_min, clip_max):
        data_range = clip_min, clip_max
        if not hasattr(self, 'view3d'):
            # too early!
            return
        self.logger.info("{}: applying clip {} <-> {}".format(self.name, clip_min, clip_max))
        self.view3d.module_manager.scalar_lut_manager.data_range = data_range
#        mlab.clf(self.scene3d.mayavi_scene)
#        self.display_scene3d()
#        mlab.draw(self.scene3d.mayavi_scene)
        self.ipw_x.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_y.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_z.module_manager.scalar_lut_manager.data_range = data_range
#        self.ipw_x.update_data()
#        self.ipw_x.update_pipeline()
#        self.ipw_y.update_data()
#        self.ipw_y.update_pipeline()
#        self.ipw_z.update_data()
#        self.ipw_z.update_pipeline()
#        self.display_scene_x()
#        self.display_scene_y()
#        self.display_scene_z()
        self.update_data_value()
        self.redraw_axis_names()

    def enable_colorbar(self, enable):
        self.logger.debug("{}: colorbar={}".format(self.name, enable))
        self.view3d.module_manager.scalar_lut_manager.show_scalar_bar = enable

    def set_colormap(self, colormap):
        self.logger.debug("{}: colormap={}".format(self.name, colormap))
        self.view3d.module_manager.scalar_lut_manager.lut_mode = colormap
        self.ipw_x.module_manager.scalar_lut_manager.lut_mode = colormap
        self.ipw_y.module_manager.scalar_lut_manager.lut_mode = colormap
        self.ipw_z.module_manager.scalar_lut_manager.lut_mode = colormap

    def get_local_min(self):
        return float(self.data.min())

    def get_local_max(self):
        return float(self.data.max())

    def get_locate_value(self):
        if self.locate_mode == LOCATE_MODE_MIN:
            return self.get_local_min()
        elif self.locate_mode == LOCATE_MODE_MAX:
            return self.get_local_max()
        elif self.locate_mode == LOCATE_MODE_VALUE:
            return self.locate_value

    def locate_nearest(self):
        data = self.data
        diff = abs(data - self.locate_value)
        position = np.unravel_index(diff.argmin(), diff.shape)
        self.goto_position(position)
        value = float(data[position])
        self.locate_value = value

    def goto_position(self, position):
        if len(position) == 2:
            self.x_index, self.y_index = position
        else:
            self.x_index, self.y_index, self.z_index = position

    def locate_sign(self, sign):
        self.locate_mode = LOCATE_MODE_VALUE
        data = self.data
        diff = sign * (data - self.locate_value)
        diff =  np.where(diff <= 0, diff.max() + 1, diff)
        n = 1
        for d in diff.shape:
            n *= d
        l = diff.reshape((n, )).argsort()
        for i in l:
            position = np.unravel_index(i, data.shape)
            break
        else:
            # not found
            return
        value = float(data[position])
        if (sign > 0 and value > self.locate_value) or (sign < 0 and value < self.locate_value):
            self.locate_value = value
            self.goto_position(position)

    def locate_next(self):
        self.locate_sign(+1)

    def locate_prev(self):
        self.locate_sign(-1)

    def set_locate_range(self):
        self.locate_low = self.get_local_min()
        self.locate_high = self.get_local_max()


    ### D e f a u l t s :
    def _locate_value_default(self):
        if self.locate_mode == LOCATE_MODE_MIN:
            return self.get_local_min()
        elif self.locate_mode == LOCATE_MODE_MAX:
            return self.get_local_max()
        elif self.locate_mode == LOCATE_MODE_VALUE:
            if self.controller.attributes["locate_value"] is not None:
                return self.controller.attributes["locate_value"]
            else:
                return self.get_local_max()

    def _clip_min_default(self):
        return self.get_local_min()

    def _clip_max_default(self):
        return self.get_local_max()

    def _x_index_default(self):
        return self.data.shape[0] // 2
    
    def _y_index_default(self):
        return self.data.shape[1] // 2
    
    def _z_index_default(self):
        if len(self.data.shape) > 2:
            return self.data.shape[2] // 2
        else:
            return 0
    
    def _data_value_default(self):
        return self.get_data_value()

    def _data_src3d_default(self):
        return mlab.pipeline.scalar_field(self.data,
                            figure=self.scene3d.mayavi_scene)

    def make_ipw_3d(self, axis_name):
        ipw = mlab.pipeline.image_plane_widget(self.data_src3d,
                        figure=self.scene3d.mayavi_scene,
                        plane_orientation='%s_axes' % axis_name)
        return ipw

    def _ipw_3d_x_default(self):
        return self.make_ipw_3d('x')

    def _ipw_3d_y_default(self):
        return self.make_ipw_3d('y')

    def _ipw_3d_z_default(self):
        return self.make_ipw_3d('z')


    def on_change_axis(self, axis_name):
        # check value
        index_name = "{}_index".format(axis_name)
        axis_number = self.controller.LOCAL_AXIS_NUMBERS[axis_name]
        index_value = getattr(self, index_name)
        shape = self.data_src3d.scalar_data.shape
        index_low = 0
        index_high = shape[axis_number] - 1
        if index_value < index_low:
            index_value = index_low
            setattr(self, index_name, index_value)
            return
        elif index_value > index_high:
            index_value = index_high
            setattr(self, index_name, index_value)
            return
        # log:
        self.log_trait_change(index_name)
        # feedback:
        self.feedback_attribute(index_name)
        getattr(self, 'ipw_3d_{}'.format(axis_name)).ipw.slice_position = \
            index_value + 1
        self.update_data_value()

    @on_trait_change('x_index')
    def on_change_x_index(self):
        self.on_change_axis('x')

    @on_trait_change('y_index')
    def on_change_y_index(self):
        self.on_change_axis('y')

    @on_trait_change('z_index')
    def on_change_z_index(self):
        self.on_change_axis('z')

    @on_trait_change('locate_mode')
    def on_change_locate_mode(self):
        self.log_trait_change("locate_mode")
        self.locate_mode_is_value = (self.locate_mode == LOCATE_MODE_VALUE)
        self.locate_value = self.get_locate_value()

    @on_trait_change('locate_value')
    def on_change_locate_value(self):
        self.log_trait_change("locate_value")
        self.locate_nearest()

    @on_trait_change('locate_nearest_button')
    def on_change_locate_nearest_button(self):
        self.log_trait_change("locate_nearest_button")
        self.locate_nearest()

    @on_trait_change('locate_prev_button')
    def on_change_locate_prev_button(self):
        self.log_trait_change("locate_prev_button")
        self.locate_prev()

    @on_trait_change('locate_next_button')
    def on_change_locate_next_button(self):
        self.log_trait_change("locate_next_button")
        self.locate_next()

    #---------------------------------------------------------------------------
    # Scene activation callbaks
    #---------------------------------------------------------------------------
    @on_trait_change('scene3d.activated')
    def display_scene3d(self):
        self.view3d = mlab.pipeline.outline(
            self.data_src3d,
            figure=self.scene3d.mayavi_scene,
        )
        self.set_locate_range()
        self.scene3d.mlab.view(40, 50)
        # Interaction properties can only be changed after the scene
        # has been created, and thus the interactor exists
        for ipw in (self.ipw_3d_x, self.ipw_3d_y, self.ipw_3d_z):
            # Turn the interaction off
            ipw.ipw.interaction = 0
        self.scene3d.scene.background = (0, 0, 0)
        # Keep the view always pointing up
        self.scene3d.scene.interactor.interactor_style = \
                                 tvtk.InteractorStyleTerrain()


    def make_side_view(self, axis_name):
        scene = getattr(self, 'scene_%s' % axis_name)

        # To avoid copying the data, we take a reference to the
        # raw VTK dataset, and pass it on to mlab. Mlab will create
        # a Mayavi source from the VTK without copying it.
        # We have to specify the figure so that the data gets
        # added on the figure we are interested in.
        outline = mlab.pipeline.outline(
                            self.data_src3d.mlab_source.dataset,
                            figure=scene.mayavi_scene,
                            )
        ipw = mlab.pipeline.image_plane_widget(
                            outline,
                            plane_orientation='%s_axes' % axis_name)
        setattr(self, 'ipw_%s' % axis_name, ipw)

        # Synchronize positions between the corresponding image plane
        # widgets on different views.
        ipw.ipw.sync_trait('slice_position',
                            getattr(self, 'ipw_3d_%s'% axis_name).ipw)

        # Make left-clicking create a crosshair
        ipw.ipw.left_button_action = 0
        # Add a callback on the image plane widget interaction to
        # move the others
        def move_view(obj, evt):
            position = obj.GetCurrentCursorPosition()
            for other_axis, axis_number in self.controller.LOCAL_AXIS_NUMBERS.iteritems():
                ipw3d = getattr(self, 'ipw_3d_{}'.format(other_axis))
                if other_axis == axis_name:
                    axis_index_value = int(round(ipw3d.ipw.slice_position)) - 1
                else:
                    axis_index_value = int(round(position[axis_number]))
                axis_index_name = '{}_index'.format(other_axis)
                setattr(self, axis_index_name, axis_index_value)
                if other_axis == axis_name:
                    continue
                ipw3d.ipw.slice_position = position[axis_number]
                #setattr(self, '{}_index'.format(other_axis), int(round(position[axis_number])))

        ipw.ipw.add_observer('InteractionEvent', move_view)
        ipw.ipw.add_observer('StartInteractionEvent', move_view)

        # Center the image plane widget
        ipw.ipw.slice_position = getattr(self, "{}_index".format(axis_name))

        # Position the view for the scene
        views = dict(x=( 0, 90),
                     y=(90, 90),
                     z=( 0,  0),
                     )
        scene.mlab.view(*views[axis_name])
        # 2D interaction: only pan and zoom
        scene.scene.interactor.interactor_style = \
                                 tvtk.InteractorStyleImage()
        scene.scene.background = (0, 0, 0)

        # Some text:
        setattr(self, "_{}_label".format(axis_name), self.draw_axis_name(axis_name))

    def draw_axis_name(self, axis_name):
        global_axis_name = self.controller.get_global_axis_name(axis_name)
        if global_axis_name == 'w':
            width = 0.06
        else:
            width = 0.04
        t = mlab.text(0.01, 0.9, global_axis_name, width=width, color=(1, 0, 0))
        return t

    def redraw_axis_names(self):
        for local_axis_name in self.controller.LOCAL_AXIS_NAMES:
            global_axis_name = self.controller.get_global_axis_name(local_axis_name)
            text = getattr(self, "_{}_label".format(local_axis_name))
            text.text = global_axis_name
            if global_axis_name == 'w':
                width = 0.06
            else:
                width = 0.04
            text.width = width

    @on_trait_change('scene_x.activated')
    def display_scene_x(self):
        return self.make_side_view('x')

    @on_trait_change('scene_y.activated')
    def display_scene_y(self):
        return self.make_side_view('y')

    @on_trait_change('scene_z.activated')
    def display_scene_z(self):
        return self.make_side_view('z')


    #---------------------------------------------------------------------------
    # The layout of the dialog created
    #---------------------------------------------------------------------------
    view = View(
        HGroup(
            Group(
                Item('scene_y',
                    editor=SceneEditor(scene_class=Scene),
                    height=SCENE_HEIGHT, width=SCENE_WIDTH,
                    resizable=True,
                ),
                Item('scene_z',
                    editor=SceneEditor(scene_class=Scene),
                    height=SCENE_HEIGHT, width=SCENE_WIDTH,
                    resizable=True,
                ),
                show_labels=False,
            ),
            Group(
                Item('scene_x',
                    editor=SceneEditor(scene_class=Scene),
                    height=SCENE_HEIGHT, width=SCENE_WIDTH,
                    resizable=True,
                ),
                Item('scene3d',
                    editor=SceneEditor(scene_class=MayaviScene),
                    height=SCENE_HEIGHT, width=SCENE_WIDTH,
                    resizable=True,
                ),
                show_labels=False,
            ),
            Group(
                Item('data_value'),
                '_',
                Item(
                    'locate_mode',
                    editor=EnumEditor(values=LOCATE_MODES),
                    label="Locate mode",
                    tooltip="Set locate mode",
                ),
                Item(
                    'locate_value',
                    editor=RangeEditor(
                        enter_set=True,
                        low_name='locate_low',
                        high_name='locate_high',
                        label_width=LABEL_WIDTH,
                        format="%g",
                        mode="slider",
                        is_float=True,
                    ),
                    enabled_when='locate_mode_is_value',
                ),
                HSplit(
                        Item(
                            'locate_prev_button',
                            editor=ButtonEditor(),
                            label="Prev",
                        ),
                        Item(
                            'locate_nearest_button',
                            editor=ButtonEditor(),
                            label="Nearest",
                        ),
                        Item(
                            'locate_next_button',
                            editor=ButtonEditor(),
                            label="Next",
                        ),
                        show_labels=False,
                ),
                show_labels=True,
            ),
        ),
        handler=VolumeSlicerHandler(),
        height=WINDOW_HEIGHT, width=WINDOW_WIDTH,
        resizable=True,
        title='Volume Slicer',
    )

