"""
Example of an elaborate dialog showing a multiple views on the same data, with
3 cuts synchronized.

This example shows how to have multiple views on the same data, how to
embedded multiple scenes in a dialog, and the caveat in populating them
with data, as well as how to add some interaction logic on an
ImagePlaneWidget.

The order in which things happen in this example is important, and it is
easy to get it wrong. First of all, many properties of the visualization
objects cannot be changed if there is not a scene created to view them.
This is why we put a lot of the visualization logic in the callback of
scene.activated, which is called after creation of the scene.
Second, default values created via the '_xxx_default' callback are created
lazyly, that is, when the attributes are accessed. As the establishement
of the VTK pipeline can depend on the order in which it is built, we
trigger these access by explicitely calling the attributes.
In particular, properties like scene background color, or interaction
properties cannot be set before the scene is activated.

The same data is exposed in the different scenes by sharing the VTK
dataset between different Mayavi data sources. See
the :ref:`sharing_data_between_scenes` tip for more details.

In this example, the interaction with the scene and the various elements
on it is strongly simplified by turning off interaction, and choosing
specific scene interactor styles. Indeed, non-technical users can be
confused with too rich interaction.
"""
# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
# Copyright (c) 2009, Enthought, Inc.
# License: BSD Style.

import collections
import numpy as np
import sys

from traits.api import HasTraits, Instance, Array, \
    Float, Str, Range, Enum, Bool, Int, \
    Trait, Button, \
    on_trait_change
from traitsui.api import View, Item, HGroup, Group, \
    HSplit, \
    Label, RangeEditor, EnumEditor, BooleanEditor, \
    ButtonEditor

from traitsui.menu import OKButton, UndoButton, RevertButton

from tvtk.api import tvtk
from tvtk.pyface.scene import Scene

from mayavi import mlab
from mayavi.core.api import PipelineBase, Source
from mayavi.core.ui.api import SceneEditor, MayaviScene, \
                                MlabSceneModel

from .mayavi_data import COLORMAPS
from .attributes import ColormapAttribute, \
                        ColorbarAttribute, \
                        IndexAttribute,\
                        Dimension4DAttribute, \
                        ClipAttribute, \
                        SymmetricClipAttribute, \
                        LocateValueAttribute, \
                        LocateModeAttribute, \
                        LOCATE_MODES, \
			LOCATE_MODE_VALUE, \
			LOCATE_MODE_MIN, \
			LOCATE_MODE_MAX, \
			LOCATE_MODE_DEFAULT

from .base_visualizer_impl import BaseVisualizerImpl
from ... import cubes

################################################################################
# The object implementing the dialog
class VolumeSlicer(HasTraits, BaseVisualizerImpl):
    ATTRIBUTES = collections.OrderedDict((
        ('colormap', ColormapAttribute()),
        ('colorbar', ColorbarAttribute()),
        ('w', IndexAttribute('w')),
        ('x', IndexAttribute('x')),
        ('y', IndexAttribute('y')),
        ('z', IndexAttribute('z')),
        ('clip', ClipAttribute()),
        ('clip_min', ClipAttribute()),
        ('clip_max', ClipAttribute()),
        ('clip_symmetric', SymmetricClipAttribute()),
        ('slicing_dim', Dimension4DAttribute()),
        ('locate_mode', LocateModeAttribute()),
        ('locate_value', LocateValueAttribute()),
    ))
    DIMENSIONS = "2D, 3D, ..., nD"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) >= 2)
    DESCRIPTION = """\
Show 2D slices for the given cube.
"""

    ALL = slice(None) # slice ':'

    W_HEIGHT = -330
    W_WIDTH = -400
    LABEL_WIDTH = 30
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

    # The index selectors
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

    ## slicing_dim:
    slicing_dim = Str()

    data_value = Str("")
    data_shape = Str("")
#    dimensions = Str("")

    clip = Float()
    clip_min = Float()
    clip_max = Float()
    clip_symmetric = Bool()
    clip_asymmetric = Bool()
    lut_mode = Enum(*COLORMAPS)
    colorbar = Bool()
    is4D = Bool(False)
    locate_mode = Enum(*LOCATE_MODES)
    locate_low = Float()
    locate_high = Float()
    locate_value = Range(low='locate_low', high='locate_high')
    locate_mode_is_value = Bool()
    locate_prev_button = Button()
    locate_nearest_button = Button()
    locate_next_button = Button()

    _axis_3d = ['x', 'y', 'z']
    _axis_names_3d = dict(x=0, y=1, z=2)
    _axis_4d = ['w', 'x', 'y', 'z']
    _axis_names_4d = dict(w=0, x=1, y=2, z=3)


    #---------------------------------------------------------------------------
    def __init__(self, logger, attributes, **traits):
        BaseVisualizerImpl.__init__(self, logger=logger, attributes=attributes)
        super(VolumeSlicer, self).__init__(**traits)
        self._set_slicing_dim_index() # -> force creation of self._slicing_dim_index
        self.x_low, self.y_low, self.z_low = 0, 0, 0
        rank = len(self.data.shape)
        if rank == 2:
            wh = 1
            zh = 1
            xh, yh = self.data.shape
            map_indices = self._map_indices_2d
            select_indices = self._select_indices_2d
        elif rank == 3:
            wh = 1
            xh, yh, zh = self.data.shape
            map_indices = self._map_indices_3d
            select_indices = self._select_indices_3d
        elif rank == 4:
            wh, xh, yh, zh = self.data.shape
            map_indices = self._map_indices_4d
            select_indices = self._select_indices_4d
        self.map_indices = map_indices
        self.select_indices = select_indices
        self.w_high, self.x_high, self.y_high, self.z_high = wh - 1, xh - 1, yh - 1, zh - 1
        self._axis_map_3d_to_4d = {}
        self._axis_map_4d_to_3d = {}
        self._set_axis_maps()
        # Force the creation of the image_plane_widgets:
        self.ipw_3d_x
        self.ipw_3d_y
        self.ipw_3d_z
        self.stop_clip_interaction = False

    def log_trait_change(self, traits):
        self.logger.info("changed traits: {}".format(traits))

    #---------------------------------------------------------------------------
    # Map indices
    #---------------------------------------------------------------------------
    def _set_axis_map_3d_to_4d(self):
        a4d = 0
        for a3d in 0, 1, 2:
            if a4d == self._slicing_dim_index:
                a4d += 1
            self._axis_map_3d_to_4d[self._axis_3d[a3d]] = self._axis_4d[a4d]
            a4d += 1

    def _set_axis_map_4d_to_3d(self):
        a3d = 0
        for a4d in 0, 1, 2, 3:
            if a4d == self._slicing_dim_index:
                a = ""
            else:
                a = self._axis_3d[a3d]
                a3d += 1
            self._axis_map_4d_to_3d[self._axis_4d[a4d]] = a

    def _set_axis_maps(self):
        self._set_axis_map_3d_to_4d()
        self._set_axis_map_4d_to_3d()

    def _map_indices_2d(self, x, y, z):
        return x, y

    def _map_indices_3d(self, x, y, z):
        return x, y, z

    def _map_indices_4d(self, x, y, z):
        l = [x, y, z]
        l.insert(self._slicing_dim_index, getattr(self, '{}_index'.format(self._axis_4d[self._slicing_dim_index])))
        return l

    def _select_indices_2d(self, w, x, y, z):
        return x, y

    def _select_indices_3d(self, w, x, y, z):
        return x, y, z

    def _select_indices_4d(self, w, x, y, z):
        return w, x, y, z

    def get_data(self, x, y, z):
        #print ">>>", (x, y, z), self.map_indices(x, y, z), self.select_indices(*self.map_indices(x, y, z))
        if len(self.data.shape) == 4:
            return self.data[self.select_indices(*self.map_indices(x, y, z))]
        else:
            return self.data

    def get_min(self):
        return self.data_src3d.scalar_data.min()

    def get_max(self):
        return self.data_src3d.scalar_data.max()

    def get_locate_value(self):
        if self.locate_mode == LOCATE_MODE_MIN:
            return self.get_min()
        elif self.locate_mode == LOCATE_MODE_MAX:
            return self.get_max()
        elif self.locate_mode == LOCATE_MODE_VALUE:
            return self.locate_value

    def locate_nearest(self):
        data = self.data_src3d.scalar_data
        diff = abs(data - self.locate_value)
        indices_3d = np.unravel_index(diff.argmin(), diff.shape)
        self.goto_indices(indices_3d)
        value = data[indices_3d]
        self.locate_value = value

    def goto_indices(self, indices_3d):
        if len(indices_3d) == 2:
            indices_3d = indices_3d + (0, )
        indices_4d = self.map_indices(*indices_3d)
        #print (self.w_index, self.x_index, self.y_index, self.z_index), ":::", indices_3d, "->", indices_4d
        if len(indices_4d) == 4:
            self.w_index, self.x_index, self.y_index, self.z_index = indices_4d
        elif len(indices_4d) == 3:
            self.x_index, self.y_index, self.z_index = indices_4d
        elif len(indices_4d) == 2:
            self.x_index, self.y_index = indices_4d
            
    def locate_sign(self, sign):
        self.locate_mode = LOCATE_MODE_VALUE
        data = self.data_src3d.scalar_data
        diff = sign * (data - self.locate_value)
        diff =  np.where(diff <= 0, diff.max() + 1, diff)
        n = 1
        for d in diff.shape:
            n *= d
        l = diff.reshape((n, )).argsort()
        for i in l:
            indices_3d = np.unravel_index(i, data.shape)
            break
        else:
            # not found
            return
        value = data[indices_3d]
        if (sign > 0 and value > self.locate_value) or (sign < 0 and value < self.locate_value):
            self.locate_value = value
            self.goto_indices(indices_3d)
        
    def locate_next(self):
        self.locate_sign(+1)

    def locate_prev(self):
        self.locate_sign(-1)

        
    #---------------------------------------------------------------------------
    # Default values
    #---------------------------------------------------------------------------
    def _locate_mode_default(self):
        if self.attributes["locate_mode"] is not None:
            return self.attributes["locate_mode"]
        elif self.attributes["locate_value"] is not None:
            return LOCATE_MODE_VALUE
        else:
            return LOCATE_MODE_DEFAULT

    def _locate_value_default(self):
        if self.locate_mode == LOCATE_MODE_MIN:
            return self.get_min()
        elif self.locate_mode == LOCATE_MODE_MAX:
            return self.get_max()
        elif self.locate_mode == LOCATE_MODE_VALUE:
            if self.attributes["locate_value"] is not None:
                return self.attributes["locate_value"]
            else:
                return self.get_min()
        
    def _data_src3d_default(self):
        data = self.get_data(self.ALL, self.ALL, self.ALL)
        self.set_locate_range(data)
        return mlab.pipeline.scalar_field(data,
                            figure=self.scene3d.mayavi_scene)

    def _clip_symmetric_default(self):
        if self.attributes["clip_symmetric"] is not None:
            clip_symmetric = self.attributes["clip_symmetric"]
        else:
            clip_symmetric = False
        #print "CLIP_SYMMETRIC:", clip_symmetric
        self.clip_asymmetric = not clip_symmetric
        return clip_symmetric

    def get_clips(self):
        if self.attributes["clip_min"] is not None:
            clip_min = self.attributes["clip_min"]
        elif self.attributes["clip"] is not None:
            clip_min = -abs(self.attributes["clip"])
        else:
            clip_min = self.data_src3d.scalar_data.min()
        if self.attributes["clip_max"] is not None:
            clip_max = self.attributes["clip_max"]
        elif self.attributes["clip"] is not None:
            clip_max = +abs(self.attributes["clip"])
        else:
            clip_max = self.data_src3d.scalar_data.max()
        clip = max(abs(clip_min), abs(clip_max))
        if self.clip_symmetric:
            clip_min = -clip
            clip_max = +clip
        return clip, clip_min, clip_max

    def set_clips(self):
        self.clip, self.clip_min, self.clip_max = self.get_clips()
        
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

    def make_ipw_3d(self, axis_name):
        ipw = mlab.pipeline.image_plane_widget(self.data_src3d,
                        figure=self.scene3d.mayavi_scene,
                        plane_orientation='%s_axes' % axis_name)
        return ipw

    def _data_shape_default(self):
        return 'x'.join(str(d) for d in self.data.shape)

    def _lut_mode_default(self):
        return self.attributes["colormap"]

    def _colorbar_default(self):
        return self.attributes["colorbar"]

    def _is4D_default(self):
        return len(self.data.shape) >= 4

    def _slicing_dim_default(self):
        s = self.attributes["slicing_dim"]
        if s is None:
            s = 'w'
        return s

    def _w_index_default(self):
        if self.attributes["w"] is not None:
            w = min(self.w_high - 1, max(self.w_low, self.attributes["w"]))
        else:
            w = self.w_high // 2
        return w

    def _x_index_default(self):
        if self.attributes["x"] is not None:
            x = min(self.x_high - 1, max(self.x_low, self.attributes["x"]))
        else:
            x = self.x_high // 2
        return x

    def _y_index_default(self):
        if self.attributes["y"] is not None:
            y = min(self.y_high - 1, max(self.y_low, self.attributes["y"]))
        else:
            y = self.y_high // 2
        return y

    def _z_index_default(self):
        if self.attributes["z"] is not None:
            z = min(self.z_high - 1, max(self.z_low, self.attributes["z"]))
        else:
            z = self.z_high // 2
        return z

    def _ipw_3d_x_default(self):
        return self.make_ipw_3d('x')

    def _ipw_3d_y_default(self):
        return self.make_ipw_3d('y')

    def _ipw_3d_z_default(self):
        return self.make_ipw_3d('z')

    def _make_range(self, axis_name):
        return Range('{}_low'.format(axis_name), '{}_high'.format(axis_name), '{}_index'.format(axis_name))

    def _x_range_default(self):
        return self._make_range('x')

    def _y_range_default(self):
        return self._make_range('y')

    def _z_range_default(self):
        return self._make_range('z')

    def set_data_value(self):
        self.data_value = str(self.data[self.select_indices(self.w_index, self.x_index, self.y_index, self.z_index)])
        #self.data_value = "data[{}, {}, {}, {}]={}".format(self.w_index, self.x_index, self.y_index, self.z_index,(self.data[self.select_indices(self.w_index, self.x_index, self.y_index, self.z_index)]))

    def _set_slicing_dim_index(self):
        self._slicing_dim_index = self.ATTRIBUTES['slicing_dim'].index(self.slicing_dim)

    def set_data_range(self):
        data_range = self.clip_min, self.clip_max
        self.view3d.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_x.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_y.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_z.module_manager.scalar_lut_manager.data_range = data_range

    def set_locate_range(self, data=None):
        if data is None:
            data = self.data_src3d.scalar_data
        self.locate_low = data.min()
        self.locate_high = data.max()

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

    @on_trait_change('clip')
    def on_change_clip(self):
        self.log_trait_change("clip")
        if self.stop_clip_interaction:
            return
        if self.clip_symmetric:
            self.stop_clip_interaction = True
            try:
                self.clip_min = -abs(self.clip)
                self.clip_max = +abs(self.clip)
            finally:
                self.stop_clip_interaction = False
        self.set_data_range()

    @on_trait_change('clip_min')
    def on_change_clip_min(self):
        self.log_trait_change("clip_min")
        if self.stop_clip_interaction:
            return
        if self.clip_symmetric:
            self.clip = abs(self.clip_min)
        else:
            self.clip = max(abs(self.clip_min), abs(self.clip_max))
#            self.stop_clip_interaction = True
#            try:
#                self.clip_min = -abs(self.clip_min)
#                self.clip_max = +abs(self.clip_min)
#            finally:
#                self.stop_clip_interaction = False
#        self.set_data_range()

    @on_trait_change('clip_max')
    def on_change_clip_max(self):
        self.log_trait_change("clip_max")
        if self.stop_clip_interaction:
            return
        if self.clip_symmetric:
            self.clip = abs(self.clip_max)
        else:
            self.clip = max(abs(self.clip_min), abs(self.clip_max))
#            self.stop_clip_interaction = True
#            try:
#                self.clip_min = -abs(self.clip_max)
#                self.clip_max = +abs(self.clip_max)
#            finally:
#                self.stop_clip_interaction = False
#        self.set_data_range()

        
    @on_trait_change('clip_symmetric')
    def on_change_clip_symmetric(self):
        self.log_trait_change("clip_symmetric")
        self.clip_asymmetric = not self.clip_symmetric
        if self.stop_clip_interaction:
            return
        if self.clip_symmetric:
            #abs_clip_min, abs_clip_max = abs(self.clip_min), abs(self.clip_max)
            #abs_clip = max(abs_clip_min, abs_clip_max)
            abs_clip = self.clip
            self.stop_clip_interaction = True
            try:
                self.clip_min = -abs_clip
                self.clip_max = +abs_clip
            finally:
                self.stop_clip_interaction = False
        self.set_data_range()

    @on_trait_change('slicing_dim')
    def on_change_slicing_dim(self):
        self.log_trait_change("slicing_dim")
        self._set_slicing_dim_index()
        self._set_axis_maps()
        data = self.get_data(self.ALL, self.ALL, self.ALL)
        self.data_src3d.scalar_data = data
        data_range = self.clip_min, self.clip_max
        self.view3d.module_manager.scalar_lut_manager.data_range = data_range
        mlab.clf(self.scene3d.mayavi_scene)
        self.display_scene3d()
        mlab.draw(self.scene3d.mayavi_scene)
        self.ipw_x.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_y.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_z.module_manager.scalar_lut_manager.data_range = data_range
        self.ipw_x.update_data()
        self.ipw_x.update_pipeline()
        self.ipw_y.update_data()
        self.ipw_y.update_pipeline()
        self.ipw_z.update_data()
        self.ipw_z.update_pipeline()
        self.display_scene_x()
        self.display_scene_y()
        self.display_scene_z()
        self.set_data_value()
        self.redraw_axis_names()

    @on_trait_change('lut_mode,colorbar')
    def on_change_lut_mode(self):
        self.log_trait_change("lut_mode,colorbar")
        self.view3d.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.view3d.module_manager.scalar_lut_manager.show_scalar_bar = self.colorbar
        self.ipw_x.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_y.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_z.module_manager.scalar_lut_manager.lut_mode = self.lut_mode

    def on_change_index_4d(self, index_4d):
        # check value
        index_value = getattr(self, '{}_index'.format(index_4d))
        index_low = getattr(self, '{}_low'.format(index_4d))
        index_high = getattr(self, '{}_high'.format(index_4d))
        if index_value < index_low:
            index_value = index_low
            setattr(self, '{}_index'.format(index_4d), index_value)
            return
        elif index_value > index_high:
            index_value = index_high
            setattr(self, '{}_index'.format(index_4d), index_value)
            return
        index_3d = self._axis_map_4d_to_3d[index_4d]
        if index_3d:
            getattr(self, 'ipw_3d_{}'.format(index_3d)).ipw.slice_position = \
                index_value + 1
            self.set_data_value()
        else:
            ## slicing dim
            sel_indices = [self.ALL, self.ALL, self.ALL]
            slicing_index = getattr(self, '{}_index'.format(self._axis_4d[self._slicing_dim_index]))
            sel_indices.insert(self._slicing_dim_index, slicing_index)
            data = self.data[self.select_indices(*sel_indices)]
            self.data_src3d.scalar_data = data
            self.locate_low = data.min()
            self.locate_high = data.max()
            #data_range = data.min(), data.max()
            #self.view3d.module_manager.scalar_lut_manager.data_range = data_range
            #self.ipw_x.module_manager.scalar_lut_manager.data_range = data_range
            #self.ipw_y.module_manager.scalar_lut_manager.data_range = data_range
            #self.ipw_z.module_manager.scalar_lut_manager.data_range = data_range
            
            self.data_src3d.update()
            self.set_clips()
            self.set_data_range()
            self.set_data_value()
            self.locate_value = self.get_locate_value()

    @on_trait_change('w_index')
    def on_change_w_index(self):
        self.log_trait_change("w_index")
        self.on_change_index_4d('w')
        
    @on_trait_change('x_index')
    def on_change_x_index(self):
        self.log_trait_change("x_index")
        self.on_change_index_4d('x')
        
    @on_trait_change('y_index')
    def on_change_y_index(self):
        self.log_trait_change("y_index")
        self.on_change_index_4d('y')
        
    @on_trait_change('z_index')
    def on_change_z_index(self):
        self.log_trait_change("z_index")
        self.on_change_index_4d('z')
        
    #---------------------------------------------------------------------------
    # Scene activation callbaks
    #---------------------------------------------------------------------------
    @on_trait_change('scene3d.activated')
    def display_scene3d(self):
        self.log_trait_change("scene3d.activated")
        self.view3d = mlab.pipeline.outline(self.data_src3d,
                        figure=self.scene3d.mayavi_scene,
                        )
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
        self.set_data_value()
        self.on_change_lut_mode()
        self.set_data_range()


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
            for other_axis, axis_number in self._axis_names_3d.iteritems():
                other_axis_4d = self._axis_map_3d_to_4d[other_axis]
                axis_index_name = "{}_index".format(other_axis_4d)
                ipw3d = getattr(self, 'ipw_3d_%s' % other_axis)
                if other_axis == axis_name:
                    axis_index_value = int(round(ipw3d.ipw.slice_position)) - 1
                else:
                    axis_index_value = int(round(position[axis_number]))
                setattr(self, axis_index_name, axis_index_value)
                if other_axis == axis_name:
                    continue
                ipw3d.ipw.slice_position = round(position[axis_number])
            self.set_data_value()

        ipw.ipw.add_observer('InteractionEvent', move_view)
        ipw.ipw.add_observer('StartInteractionEvent', move_view)

        # Center the image plane widget
        ipw.ipw.slice_position = getattr(self, '{}_index'.format(axis_name))

        # Position the view for the scene
        #views = dict(x=( 0, 90),
        #             y=(90, 90),
        #             z=( 0,  0),
        #             )
        views = dict(x=( 0,  90),
                     y=(90, -90),
                     z=( 0,   0),
                     )
        scene.mlab.view(*views[axis_name])
        # 2D interaction: only pan and zoom
        scene.scene.interactor.interactor_style = \
                                 tvtk.InteractorStyleImage()
        scene.scene.background = (0, 0, 0)

        # Some text:
        setattr(self, "_axis_name_3d_{}".format(axis_name), self.draw_axis_name(axis_name))

    def draw_axis_name(self, axis_name_3d):
        axis_name_4d = self._axis_map_3d_to_4d[axis_name_3d]
        if axis_name_4d == 'w':
            width = 0.06
        else:
            width = 0.04
        t = mlab.text(0.01, 0.9, axis_name_4d, width=width, color=(1, 0, 0))
        return t

    def redraw_axis_names(self):
        for axis_name_3d in self._axis_3d:
            text = getattr(self, "_axis_name_3d_{}".format(axis_name_3d))
            axis_name_4d = self._axis_map_3d_to_4d[axis_name_3d]
            text.text = axis_name_4d
            if axis_name_4d == 'w':
                width = 0.06
            else:
                width = 0.04
            text.width = width

    @on_trait_change('scene_x.activated')
    def display_scene_x(self):
        self.log_trait_change("scene_x.activated")
        return self.make_side_view('x')

    @on_trait_change('scene_y.activated')
    def display_scene_y(self):
        self.log_trait_change("scene_y.activated")
        return self.make_side_view('y')

    @on_trait_change('scene_z.activated')
    def display_scene_z(self):
        self.log_trait_change("scene_z.activated")
        return self.make_side_view('z')


    #---------------------------------------------------------------------------
    # The layout of the dialog created
    #---------------------------------------------------------------------------
    view = View(
        HGroup(
            Group(
                Item('scene_y',
                    editor=SceneEditor(scene_class=Scene),
                    height=W_HEIGHT, width=W_WIDTH,
                ),
                Item('scene_z',
                    editor=SceneEditor(scene_class=Scene),
                    height=W_HEIGHT, width=W_WIDTH,
                ),
                show_labels=False,
            ),
            Group(
                Item('scene_x',
                    editor=SceneEditor(scene_class=Scene),
                    height=W_HEIGHT, width=W_WIDTH,
                ),
                Item('scene3d',
                    editor=SceneEditor(scene_class=MayaviScene),
                    height=W_HEIGHT, width=W_WIDTH,
                ),
                show_labels=False,
            ),
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
                    'slicing_dim',
                    editor=EnumEditor(
                        values=['w', 'x', 'y', 'z']

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
                    'data_value',
                    label="Value",
                    style="readonly",
                    #emphasized=True,
                ),
                Item(
                    'lut_mode',
                    editor=EnumEditor(
                        values=COLORMAPS,

                    ),
                    label="Colormap",
                ),
                '_',
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
                '_',
                Item(
                    'colorbar',
                    editor=BooleanEditor(
                    ),
                    label="Colorbar",
                ),
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
                show_border=True
            ),
        ),
        #icon="rubik-logo.ico",
        resizable=True,
        title=BaseVisualizerImpl.window_title("VolumeSlicer"),
        #width=1200,
        #height=400,
        buttons=[UndoButton, OKButton, RevertButton]

    )


if __name__ == "__main__":
    ################################################################################
    # Create some data
    x, y, z = np.ogrid[-5:5:64j, -5:5:64j, -5:5:64j]
    data = np.sin(3*x)/x + 0.05*z**2 + np.cos(3*y)
    
    m = VolumeSlicer(data=data)
    m.configure_traits()
