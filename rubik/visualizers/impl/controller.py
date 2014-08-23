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
import threading

from traits.api import \
    HasTraits, on_trait_change, \
    Int, Str, Bool, \
    Range
   
from traitsui.api import \
    View, Item, HGroup, Group, \
    RangeEditor, EnumEditor

from .base_controller_impl import BaseControllerImpl

from .attributes import \
    IndexAttribute
    
class ThreadedView(threading.Thread):
    def __init__(self, viewer):
        threading.Thread.__init__(self)
        self.viewer = viewer

    def run(self):
        self.viewer.configure_traits()


class BaseController(HasTraits, BaseControllerImpl):
    def __init__(self, logger, attributes, **traits):
        BaseControllerImpl.__init__(self, logger=logger, attributes=attributes)
        HasTraits.__init__(self, **traits)
        self.viewers = []

    def apply(self):
        for attribute_name in self.ATTRIBUTES:
            self.apply_attribute(attribute_name)

    def apply_attribute(self, attribute_name):
        for viewer in self.viewers:
            setattr(viewer, attribute_name, getattr(self, attribute_name))
            
    def run(self):
        threads = []
        for viewer in self.viewers:
            viewer.edit_traits()
        self.configure_traits()

class Controller(BaseController):
    ATTRIBUTES = collections.OrderedDict((
        ('w', IndexAttribute('w')),
        ('x', IndexAttribute('x')),
        ('y', IndexAttribute('y')),
        ('z', IndexAttribute('z')),
        ('slicing_axis', IndexAttribute('w')),
    ))
    DIMENSIONS = "2D, 3D, ..., nD"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) >= 2)
    DESCRIPTION = """\
Controller for multiple viewers
"""
    LABEL_WIDTH = 30
    AXIS_NAMES = ['w', 'x', 'y', 'z']
    AXIS_NUMBERS = dict((axis_name, axis_number) for axis_number, axis_name in enumerate(AXIS_NAMES))
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


    def __init__(self, logger, attributes, **traits):
        super(Controller, self).__init__(logger=logger, attributes=attributes, **traits)
        self.w_low, self.x_low, self.y_low, self.z_low = 0, 0, 0, 0
        rank = len(self.data.shape)
        if rank == 2:
            wh = 1
            zh = 1
            xh, yh = self.data.shape
        elif rank == 3:
            wh = 1
            xh, yh, zh = self.data.shape
        elif rank == 4:
            wh, xh, yh, zh = self.data.shape
        self.w_high, self.x_high, self.y_high, self.z_high = wh - 1, xh - 1, yh - 1, zh - 1


    ### U t i l i t i e s :
    def create_viewer(self, viewer_class):
        return viewer_class(controller=self, data=self.get_volume())

    def add_viewer(self, viewer_class):
        viewer = self.create_viewer(viewer_class)
        self.viewers.append(viewer)
        return viewer
     

    def get_volume(self):
        if len(self.data.shape) == 4:
            s = [self.S_ALL, self.S_ALL, self.S_ALL]
            s.insert(self.AXIS_NUMBERS[self.slicing_axis], getattr(self, '{}_index'.format(self.slicing_axis)))
            return self.data[s]
        else:
            return self.data

    ### D e f a u l t s :
    def _data_shape_default(self):
        return 'x'.join(str(d) for d in self.data.shape)

    def _is4D_default(self):
        return len(self.data.shape) == 4

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
            slicing_axis = self.AXIS_NAMES[0]
        return slicing_axis

    ### T r a t s   c h a n g e s :
    @on_trait_change('w_index')
    def on_change_w_index(self):
        self.log_trait_change('w_index')

    @on_trait_change('x_index')
    def on_change_x_index(self):
        self.log_trait_change('x_index')

    @on_trait_change('y_index')
    def on_change_y_index(self):
        self.log_trait_change('y_index')

    @on_trait_change('z_index')
    def on_change_z_index(self):
        self.log_trait_change('z_index')
       

    controller_view = View(
        HGroup(
            Group(
                Item(
                    'data_shape',
                    label="Shape",
                    style="readonly",
                ),
#                Item(
#                    'dimensions',
#                    label="Dimensions",
#                    style="readonly",
#                ),
                Item(
                    'slicing_axis',
                    editor=EnumEditor(
                        values=AXIS_NAMES

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
            ),
        ),
    )
