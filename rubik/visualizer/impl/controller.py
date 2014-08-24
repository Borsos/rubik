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
    'Controller',
]

import collections

from traits.api import \
    HasTraits, on_trait_change, \
    Int, Str, Bool, Float, \
    Range, Instance

   
from traitsui.api import \
    View, Item, HGroup, Group, \
    Action, \
    RangeEditor, EnumEditor, BooleanEditor

from traitsui.menu import OKButton, UndoButton, RevertButton
from traitsui.handler import Controller as TraitsController

from .base_controller_impl import BaseControllerImpl
from .base_handler_mixin import BaseHandlerMixIn

from .mayavi_data import \
    COLORMAPS

from .attributes import \
    IndexAttribute, \
    Dimension4DAttribute, \
    ColormapAttribute, \
    ColorbarAttribute, \
    ClipAttribute, \
    AutoClipAttribute, \
    SymmetricClipAttribute, \
    LocateModeAttribute, \
    LocateValueAttribute

    
class ControllerHandler(TraitsController, BaseHandlerMixIn):
    def init(self, info):
        TraitsController.init(self, info)
        BaseHandlerMixIn.init(self, info)

    def get_title(self):
        return Controller.default_window_title()

    def _on_close(self, info):
        BaseHandlerMixIn._on_close(self, info)
        #info.object.close_ui()


class Controller(HasTraits, BaseControllerImpl):
    ATTRIBUTES = collections.OrderedDict((
        ('w', IndexAttribute('w')),
        ('x', IndexAttribute('x')),
        ('y', IndexAttribute('y')),
        ('z', IndexAttribute('z')),
        ('colormap', ColormapAttribute()),
        ('colorbar', ColorbarAttribute()),
        ('slicing_axis', Dimension4DAttribute()),
        ('clip', ClipAttribute()),
        ('clip_min', ClipAttribute()),
        ('clip_max', ClipAttribute()),
        ('clip_auto', AutoClipAttribute()),
        ('clip_symmetric', SymmetricClipAttribute()),
# passed to views
        ('locate_mode', LocateModeAttribute()),
        ('locate_value', LocateValueAttribute()),
    ))
    DIMENSIONS = "2D, 3D, ..., nD"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) >= 2)
    DESCRIPTION = """\
Controller for multiple views
"""
    LABEL_WIDTH = 30
    LOCAL_AXIS_NAMES = ['x', 'y', 'z']
    LOCAL_AXIS_NUMBERS = dict((axis_name, axis_number) for axis_number, axis_name in enumerate(LOCAL_AXIS_NAMES))
    GLOBAL_AXIS_NAMES = ['w', 'x', 'y', 'z']
    GLOBAL_AXIS_NUMBERS = dict((axis_name, axis_number) for axis_number, axis_name in enumerate(GLOBAL_AXIS_NAMES))
    S_ALL = slice(None, None, None)

    # The axis selectors
    ## w:
    w_low = Int(0)
    w_high = Int(0)
    w_index = Int(0)
    w_range = Range(low='w_low', high='w_high', value='w_index')
    ## x:
    x_low = Int
    x_high = Int
    x_index = Int
    x_range = Range(low='x_low', high='x_high', value='x_index')
    ## y:
    y_low = Int(0)
    y_high = Int(0)
    y_index = Int(0)
    y_range = Range(low='y_low', high='y_high', value='y_index')
    ## z:
    z_low = Int(0)
    z_high = Int(0)
    z_index = Int(0)
    z_range = Range(low='z_low', high='z_high', value='z_index')
    ## is4D:
    is4D = Bool()

    slicing_axis = Str("")
    data_shape = Str("")
    close_button = Action(name='Close', action='_on_close')

    colorbar = Bool()
    colormap = Str()

    data_min = Float()
    data_max = Float()

    clip = Float()
    clip_min = Float()
    clip_max = Float()
    clip_auto = Bool()
    clip_symmetric = Bool()
    clip_readonly = Bool()
    clip_visible = Bool()
    clip_range_readonly = Bool()
    clip_range_visible = Bool()

    def __init__(self, logger, attributes, **traits):
        HasTraits.__init__(self, **traits)
        BaseControllerImpl.__init__(self, logger=logger, attributes=attributes)
        self.w_low, self.x_low, self.y_low, self.z_low = 0, 0, 0, 0
        rank = len(self.shape)
        if rank == 2:
            wh = 1
            zh = 1
            xh, yh = self.shape
        elif rank == 3:
            wh = 1
            xh, yh, zh = self.shape
        elif rank == 4:
            wh, xh, yh, zh = self.shape
        self.w_high, self.x_high, self.y_high, self.z_high = wh - 1, xh - 1, yh - 1, zh - 1
        self.set_default_clips()
        self.set_axis_mapping()


    ### U t i l i t i e s :
    def create_view(self, view_class, data):
        return view_class(controller=self, data=data)

    def add_view(self, view_class, data):
        if data.shape != self.shape:
            raise ValueError("{}: cannot create {} view: data shape {} is not {}".format(self.name, view_class.__name__, data.shape, self.shape))
        local_volume = self.get_local_volume(data)
        view = self.create_view(view_class, local_volume)
        self.views.append(view)
        self.views_data[view] = data
        self.add_class_trait(view.name, Instance(view_class))
        self.add_trait(view.name, view)
        self.update_data_range()
        return view

    def update_data_range(self):
        if self.views:
            data_min_l, data_max_l = [], []
            for view in self.views:
                for local_volume in view.data:
                    data_min_l.append(local_volume.min())
                    data_max_l.append(local_volume.max())
            self.data_min = float(min(data_min_l))
            self.data_max = float(max(data_max_l))
            self.logger.info("{}: data range: {} <-> {}".format(self.name, self.data_min, self.data_max))
        else:
            self.data_min = 0.0
            self.data_max = 0.0
                
    def get_local_volume(self, data):
        if data.shape != self.shape:
            raise ValueError("{}: invalid shape {}".format(self.name, data.shape))
        if len(self.shape) == 4:
            s = [self.S_ALL, self.S_ALL, self.S_ALL]
            s.insert(self.GLOBAL_AXIS_NUMBERS[self.slicing_axis], getattr(self, '{}_index'.format(self.slicing_axis)))
            return data[s]
        else:
            return data

    def set_axis_mapping(self):
        self._m_local2global = {}
        self._m_global2local = {}
        local_axis_number = 0
        for global_axis_number, global_axis_name in enumerate(self.GLOBAL_AXIS_NAMES):
            if global_axis_name != self.slicing_axis:
                local_axis_name = self.LOCAL_AXIS_NAMES[local_axis_number]
                self._m_local2global[local_axis_name] = global_axis_name
                self._m_global2local[global_axis_name] = local_axis_name
                local_axis_number += 1

    def get_global_axis_name(self, local_axis_name):
        return self._m_local2global[local_axis_name]
        
    def get_local_axis_name(self, global_axis_name):
        return self._m_global2local[global_axis_name]
        
    def set_default_clips(self):
        clip_symmetric = self.attributes["clip_symmetric"]
        clip_auto = self.attributes["clip_auto"]
        clip = self.attributes["clip"]
        clip_min = self.attributes["clip_min"]
        clip_max = self.attributes["clip_max"]
        if clip is not None:
            self.clip = clip
        if clip_min is not None:
            self.clip_min = clip_min
        if clip_max is not None:
            self.clip_max = clip_max
        if clip_symmetric is None:
            if clip is not None:
                clip_symmetric = True
            else:
                clip_symmetric = False
        if clip_auto is None:
            if clip is None and (clip_min is None or clip_max is None):
                clip_auto = True
            else:
                clip_auto = False
        self.clip_symmetric = clip_symmetric
        self.clip_auto = clip_auto

    def close_uis(self):
        super(Controller, self).close_uis()
        # locks on exit !
        #for view in self.views:
        #    view.close_uis()
        
    ### D e f a u l t s :
    def _colorbar_default(self):
        return self.attributes["colorbar"]

    def _colormap_default(self):
        return self.attributes["colormap"]

    def _data_shape_default(self):
        return 'x'.join(str(d) for d in self.shape)

    def _is4D_default(self):
        return len(self.shape) == 4

    def _axis_index_default(self, axis_name):
        if self.attributes.get(axis_name, None) is None:
            h = getattr(self, "{}_high".format(axis_name))
            l = getattr(self, "{}_low".format(axis_name))
            return (h - l) // 2
        else:
            return self.attributes[axis_name]

    def _w_index_default(self):
        return self._axis_index_default('w')

    def _x_index_default(self):
        return self._axis_index_default('x')

    def _y_index_default(self):
        return self._axis_index_default('y')

    def _z_index_default(self):
        return self._axis_index_default('z')

    def _slicing_axis_default(self):
        slicing_axis = self.attributes.get("slicing_axis", None) 
        if slicing_axis is None:
            slicing_axis = self.GLOBAL_AXIS_NAMES[0]
        return slicing_axis

    def on_change_axis(self, global_axis_name):
        if global_axis_name == self.slicing_axis:
            self.logger.error("{}: changing the slicing axis is not supported yet".format(self.name))
            for view in self.views:
                local_volume = self.get_local_volume(self.views_data[view])
                view.set_volume(local_volume)
            self.update_data_range()
            self.update_clip_range()
        else:
            local_axis_name = self.get_local_axis_name(global_axis_name)
            self.log_trait_change('{}_index'.format(global_axis_name))
            self.apply_attribute('{}_index'.format(local_axis_name))

    def set_clip(self):
        if self.clip_auto:
            self.clip_min, self.clip_max = self.data_min, self.data_max
            self.clip = max(abs(self.clip_min), abs(self.clip_max))
        self.clip_readonly = not self.clip_auto
        self.clip_range_readonly = not self.clip_auto
        self.clip_visible = self.clip_symmetric
        self.clip_range_visible = not self.clip_symmetric

    def get_clip_range(self):
        if self.clip_auto:
            clip_min = float(self.data_min)
            clip_max = float(self.data_max)
            clip = max(abs(clip_min), abs(clip_max))
        else:
            clip_min = self.clip_min
            clip_max = self.clip_max
            clip = self.clip
        if self.clip_symmetric:
            return -clip, clip
        else:
            return clip_min, clip_max

    def update_clip_range(self):
        clip_min, clip_max = self.get_clip_range()
        self.logger.info("{}: applying clip {} <-> {}".format(self.name, clip_min, clip_max))
        for view in self.views:
            view.update_clip_range(clip_min, clip_max)

    ### T r a t s   c h a n g e s :
    @on_trait_change('colorbar')
    def on_change_colorbar(self):
        for view in self.views:
            view.enable_colorbar(self.colorbar)

    @on_trait_change('colormap')
    def on_change_colormap(self):
        for view in self.views:
            view.set_colormap(self.colormap)

    @on_trait_change('data_min,data_max')
    def on_change_data_range(self):
        self.set_clip()
        self.update_clip_range()

    @on_trait_change('clip_symmetric')
    def on_change_clip_symmetric(self):
        self.set_clip()
        self.update_clip_range()

    @on_trait_change('clip_auto')
    def on_change_clip_auto(self):
        self.set_clip()
        self.update_clip_range()

    @on_trait_change('clip')
    def on_change_clip(self):
        self.logger.debug("{}: clip: auto={}, symmetric={}, clip={}".format(self.name, self.clip_auto, self.clip_symmetric, self.clip))
        if self.clip_symmetric:
            self.update_clip_range()
     
    @on_trait_change('clip_min,clip_max')
    def on_change_clip(self):
        self.logger.debug("{}: clip: auto={}, symmetric={}, clip_min={}, clip_max={}".format(self.name, self.clip_auto, self.clip_symmetric, self.clip_min, self.clip_max))
        if not self.clip_symmetric:
            self.update_clip_range()
     
    @on_trait_change('w_index')
    def on_change_w_index(self):
        self.on_change_axis('w')

    @on_trait_change('x_index')
    def on_change_x_index(self):
        self.on_change_axis('x')

    @on_trait_change('y_index')
    def on_change_y_index(self):
        self.on_change_axis('y')

    @on_trait_change('z_index')
    def on_change_z_index(self):
        self.on_change_axis('z')
       

    controller_view = View(
        HGroup(
            Group(
                Item(
                    'data_shape',
                    label="Shape",
                    style="readonly",
                ),
                Item(
                    'slicing_axis',
                    editor=EnumEditor(
                        values=GLOBAL_AXIS_NAMES

                    ),
                    label="Slicing dim",
                    enabled_when='is4D',
                    visible_when='is4D',
                    #emphasized=True,
                    style="readonly",
                    tooltip="the slicing dimension",
                    help="4D volumes are sliced along the 'slicing dimension'; it is possible to change the value of this dimension using the related slider",
                ),
                Item(
                    '_',
                    enabled_when='is4D',
                    visible_when='is4D',
                ),
                Item(
                    'w_index',
                    editor=RangeEditor(
                        enter_set=True,
                        low_name='w_low',
                        high_name='w_high',
                        format="%d",
                        label_width=LABEL_WIDTH,
                        mode="auto",
                    ),
                    enabled_when='is4D',
                    visible_when='is4D',
                    tooltip="the w dimension",
                ),
                Item(
                    'x_index',
                    editor=RangeEditor(
                        enter_set=True,
                        low_name='x_low',
                        high_name='x_high',
                        format="%d",
                        label_width=LABEL_WIDTH,
                        mode="slider",
                    ),
                    format_str="%<8s",
                    tooltip="the x dimension",
                ),
                Item(
                    'y_index',
                    editor=RangeEditor(
                        enter_set=True,
                        low_name='y_low',
                        high_name='y_high',
                        format="%d",
                        label_width=LABEL_WIDTH,
                        mode="slider",
                    ),
                    format_str="%<8s",
                    tooltip="the y dimension",
                ),
                Item(
                    'z_index',
                    editor=RangeEditor(
                        enter_set=True,
                        low_name='z_low',
                        high_name='z_high',
                        format="%d",
                        label_width=LABEL_WIDTH,
                        mode="slider",
                    ),
                    format_str="%<8s",
                    tooltip="the z dimension",
                ),
                '_',
                Item(
                    'colorbar',
                    editor=BooleanEditor(
                    ),
                    label="Colorbar",
                ),
                Item(
                    'colormap',
                    editor=EnumEditor(
                        values=COLORMAPS,

                    ),
                    label="Colormap",
                ),
                '_',
                Item(
                    'data_min',
                    label="Data min",
                    style="readonly",
                ),
                Item(
                    'data_max',
                    label="Data max",
                    style="readonly",
                ),
                Item(
                    'clip_auto',
                    editor=BooleanEditor(),
                    label="Automatic",
                    tooltip="makes clip automatic",
                    help="if set, clip is taken from data range"
                ),
                Item(
                    'clip_symmetric',
                    editor=BooleanEditor(),
                    label="Symmetric",
                    tooltip="makes clip symmetric",
                    help="if set, clip_min=-clip, clip_max=+clip",
                ),
                Item(
                    'clip',
                    label="Clip",
                    visible_when='clip_visible',
                    enabled_when='clip_readonly',
                ),
                Item(
                    'clip_min',
                    label="Clip min",
                    visible_when='clip_range_visible',
                    enabled_when='clip_range_readonly',
                ),
                Item(
                    'clip_max',
                    label="Clip max",
                    visible_when='clip_range_visible',
                    enabled_when='clip_range_readonly',
                ),

            ),
        ),
        buttons=[UndoButton, RevertButton, close_button],
        handler=ControllerHandler(),
        resizable=True,
        title="untitled",
    )
