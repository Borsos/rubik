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
    Range

from traitsui.handler import Handler
   
from traitsui.api import \
    View, Item, HGroup, Group, \
    Action, \
    RangeEditor, EnumEditor, BooleanEditor

from traitsui.menu import OKButton, UndoButton, RevertButton
from traitsui.handler import Handler

from .base_controller_impl import BaseControllerImpl

from .attributes import \
    IndexAttribute, \
    Dimension4DAttribute, \
    ClipAttribute, \
    SymmetricClipAttribute

    
class ControllerHandler(Handler):
    def _on_close(self, info):
        info.ui.dispose()

class Controller(HasTraits, BaseControllerImpl):
    ATTRIBUTES = collections.OrderedDict((
        ('w', IndexAttribute('w')),
        ('x', IndexAttribute('x')),
        ('y', IndexAttribute('y')),
        ('z', IndexAttribute('z')),
        ('slicing_axis', Dimension4DAttribute()),
        ('clip', ClipAttribute()),
        ('clip_min', ClipAttribute()),
        ('clip_max', ClipAttribute()),
        ('clip_symmetric', SymmetricClipAttribute()),
    ))
    DIMENSIONS = "2D, 3D, ..., nD"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) >= 2)
    DESCRIPTION = """\
Controller for multiple viewers
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

    data_min = Float()
    data_max = Float()

    clip = Float()
    clip_min = Float()
    clip_max = Float()
    clip_symmetric = Bool()
    clip_asymmetric = Bool()

    def __init__(self, logger, attributes, **traits):
        BaseControllerImpl.__init__(self, logger=logger, attributes=attributes)
        HasTraits.__init__(self, **traits)
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
        self.set_axis_mapping()


    ### U t i l i t i e s :
    def create_viewer(self, viewer_class, data):
        return viewer_class(controller=self, data=data)

    def add_viewer(self, viewer_class, data):
        if data.shape != self.shape:
            raise ValueError("{}: cannot create {} viewer: data shape {} is not {}".format(self.name, viewer_class.__name__, data.shape, self.shape))
        local_volume = self.get_local_volume(data)
        viewer = self.create_viewer(viewer_class, local_volume)
        self.viewers.append(viewer)
        self.viewers_data[viewer] = data
        self.add_trait(viewer.name, viewer)
        self.update_data_range()
        return viewer

    def update_data_range(self):
        if self.viewers:
            data_min_l, data_max_l = [], []
            for viewer in self.viewers:
                for local_volume in viewer.data:
                    data_min_l.append(local_volume.min())
                    data_max_l.append(local_volume.max())
            self.data_min = float(min(data_min_l))
            self.data_max = float(max(data_max_l))
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
                print self.LOCAL_AXIS_NAMES, global_axis_name, self.slicing_axis, local_axis_number, local_axis_name
                self._m_local2global[local_axis_name] = global_axis_name
                self._m_global2local[global_axis_name] = local_axis_name
                local_axis_number += 1
        print "l2g:", self._m_local2global
        print "g2l:", self._m_global2local

    def get_global_axis_name(self, local_axis_name):
        return self._m_local2global[local_axis_name]
        
    def get_local_axis_name(self, global_axis_name):
        return self._m_global2local[global_axis_name]
        
    def get_clips(self):
        if self.attributes["clip_min"] is not None:
            clip_min = self.attributes["clip_min"]
        elif self.attributes["clip"] is not None:
            clip_min = -abs(self.attributes["clip"])
        else:
            clip_min = self.data_min
        if self.attributes["clip_max"] is not None:
            clip_max = self.attributes["clip_max"]
        elif self.attributes["clip"] is not None:
            clip_max = +abs(self.attributes["clip"])
        else:
            clip_max = self.data_max
        clip = max(abs(clip_min), abs(clip_max))
        if self.clip_symmetric:
            clip_min = -clip
            clip_max = +clip
        return clip, clip_min, clip_max

        
    ### D e f a u l t s :
    def _clip_symmetric_default(self):
        if self.attributes["clip_symmetric"] is not None:
            clip_symmetric = self.attributes["clip_symmetric"]
        else:
            clip_symmetric = False
        self.clip_asymmetric = not clip_symmetric
        return clip_symmetric

    def _clip_default(self):
        clip, clip_min, clip_max = self.get_clips()
        #print "CLIP_DEF: ", clip
        return clip

    def _clip_min_default(self):
        clip, clip_min, clip_max = self.get_clips()
        #print "CLIP_MIN: ", clip_min
        return clip_min

    def _clip_max_default(self):
        clip, clip_min, clip_max = self.get_clips()
        #print "CLIP_MAX: ", clip_max
        return clip_max

    def _data_shape_default(self):
        return 'x'.join(str(d) for d in self.shape)

    def _is4D_default(self):
        return len(self.shape) == 4

    def _axis_index_default(self, axis_name):
        if self.attributes.get(axis_name, None) is None:
            h = getattr(self, "{}_high".format(axis_name))
            l = getattr(self, "{}_low".format(axis_name))
            return (h - l + 1) // 2
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
            gmin, gmax = [], []
            for viewer in self.viewers:
                local_volume = self.get_local_volume(self.viewers_data[viewer])
                viewer.set_volume(local_volume)
                gmin.append(local_volume.min())
                gmax.append(local_volume.max())
            self.update_data_range()
            clip, clip_min, clip_max = self.get_clips()
            for viewer in self.viewers:
                viewer.update_volume(clip_min, clip_max)
        else:
            local_axis_name = self.get_local_axis_name(global_axis_name)
            self.log_trait_change('{}_index'.format(global_axis_name))
            self.apply_attribute('{}_index'.format(local_axis_name))

    ### T r a t s   c h a n g e s :
    @on_trait_change('clip_symmetric')
    def on_change_clip_symmetric(self):
        self.clip_asymmetric = not self.clip_symmetric

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
                    'clip',
                    label="Clip",
                    visible_when='clip_symmetric',
                ),
                Item(
                    'clip_min',
                    label="Clip min",
                    visible_when='clip_asymmetric',
                ),
                Item(
                    'clip_max',
                    label="Clip max",
                    visible_when='clip_asymmetric',
                ),
                Item(
                    'clip_symmetric',
                    editor=BooleanEditor(),
                    label="Symmetric",
                    tooltip="makes clip symmetric",
                    help="if set, clip_min=-clip, clip_max=+clip",
                ),

            ),
        ),
        buttons=[UndoButton, RevertButton, close_button],
        handler=ControllerHandler(),
        resizable=True,
    )
