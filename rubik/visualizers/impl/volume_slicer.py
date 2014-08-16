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

from traits.api import HasTraits, Instance, Array, \
    Float, Str, Range, Enum, Bool, Int, \
    Trait, \
    on_trait_change
from traitsui.api import View, Item, HGroup, Group, \
    Label, RangeEditor, EnumEditor, BooleanEditor \

from traitsui.menu import OKButton, UndoButton, RevertButton

from tvtk.api import tvtk
from tvtk.pyface.scene import Scene

from mayavi import mlab
from mayavi.core.api import PipelineBase, Source
from mayavi.core.ui.api import SceneEditor, MayaviScene, \
                                MlabSceneModel

from .mayavi_data import COLORMAPS
from .attributes import Colormap, Colorbar, Index, Dimension4D
from .base_visualizer_impl import BaseVisualizerImpl

################################################################################
# The object implementing the dialog
class VolumeSlicer(HasTraits, BaseVisualizerImpl):
    ATTRIBUTES = collections.OrderedDict((
        ('colormap', Colormap()),
        ('colorbar', Colorbar()),
        ('w', Index('w')),
        ('x', Index('x')),
        ('y', Index('y')),
        ('z', Index('z')),
        ('sticky_dim', Dimension4D()),
    ))
    DIMENSIONS = "2D, 3D, ..., nD"
    DATA_CHECK = classmethod(lambda cls, data: len(data.shape) >= 2)
    DESCRIPTION = """\
Show 2D slices for the given cube.
"""

    ALL = slice(None) # slice ':'

    W_HEIGHT = -330
    W_WIDTH = -400
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

    ## sticky_dim:
    sticky_dim = Str()

    data_value = Str("")
    data_shape = Str("")
#    dimensions = Str("")

    lut_mode = Enum(*COLORMAPS)
    colorbar = Bool()
    is4D = Bool(False)

    _axis_3d = ['x', 'y', 'z']
    _axis_names_3d = dict(x=0, y=1, z=2)
    _axis_4d = ['w', 'x', 'y', 'z']
    _axis_names_4d = dict(w=0, x=1, y=2, z=3)


    #---------------------------------------------------------------------------
    def __init__(self, logger, attributes, **traits):
        BaseVisualizerImpl.__init__(self, logger=logger, attributes=attributes)
        super(VolumeSlicer, self).__init__(**traits)
        self._set_sticky_dim_index() # -> force creation of self._sticky_dim_index
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

    #---------------------------------------------------------------------------
    # Map indices
    #---------------------------------------------------------------------------
    def _set_axis_map_3d_to_4d(self):
        a4d = 0
        for a3d in 0, 1, 2:
            if a4d == self._sticky_dim_index:
                a4d += 1
            self._axis_map_3d_to_4d[self._axis_3d[a3d]] = self._axis_4d[a4d]
            a4d += 1

    def _set_axis_map_4d_to_3d(self):
        a3d = 0
        for a4d in 0, 1, 2, 3:
            if a4d == self._sticky_dim_index:
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
        l.insert(self._sticky_dim_index, getattr(self, '{}_index'.format(self._axis_4d[self._sticky_dim_index])))
        return l

    def _select_indices_2d(self, w, x, y, z):
        return x, y

    def _select_indices_3d(self, w, x, y, z):
        return x, y, z

    def _select_indices_4d(self, w, x, y, z):
        return w, x, y, z

    def get_data(self, x, y, z):
        #print ">>>", (x, y, z), self.map_indices(x, y, z), self.select_indices(*self.map_indices(x, y, z))
        return self.data[self.select_indices(*self.map_indices(x, y, z))]

    #---------------------------------------------------------------------------
    # Default values
    #---------------------------------------------------------------------------
    def _data_src3d_default(self):
        if len(self.data.shape) == 4:
            data = self.get_data(self.ALL, self.ALL, self.ALL)
        else:
            data = self.data
        return mlab.pipeline.scalar_field(data,
                            figure=self.scene3d.mayavi_scene)

    def make_ipw_3d(self, axis_name):
        ipw = mlab.pipeline.image_plane_widget(self.data_src3d,
                        figure=self.scene3d.mayavi_scene,
                        plane_orientation='%s_axes' % axis_name)
        return ipw

    def _data_shape_default(self):
        return 'x'.join(str(d) for d in self.data.shape)

#    def _dimensions_default(self):
#        if len(self.data.shape) == 2:
#            return "x, y"
#        elif len(self.data.shape) == 3:
#            return "x, y, z"
#        elif len(self.data.shape) == 4:
#            return "w, x, y, z"

    def _lut_mode_default(self):
        return self.attributes["colormap"]

    def _colorbar_default(self):
        return self.attributes["colorbar"]

    def _is4D_default(self):
        return len(self.data.shape) >= 4

    def _sticky_dim_default(self):
        s = self.attributes["sticky_dim"]
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

    def _set_data_value(self):
        self.data_value = str(self.data[self.select_indices(self.w_index, self.x_index, self.y_index, self.z_index)])
        #self.data_value = "data[{}, {}, {}, {}]={}".format(self.w_index, self.x_index, self.y_index, self.z_index,(self.data[self.select_indices(self.w_index, self.x_index, self.y_index, self.z_index)]))

    def _set_sticky_dim_index(self):
        self._sticky_dim_index = self.ATTRIBUTES['sticky_dim'].index(self.sticky_dim)

    @on_trait_change('sticky_dim')
    def on_change_sticky_dim(self):
        self._set_sticky_dim_index()
        self._set_axis_maps()
        if len(self.data.shape) == 4:
            data = self.get_data(self.ALL, self.ALL, self.ALL)
        else:
            data = self.data
        data_range = data.min(), data.max()
        self.data_src3d.scalar_data = data
        #self.data_src3d = mlab.pipeline.scalar_field(data,
        #     figure=self.scene3d.mayavi_scene)
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
        self._set_data_value()
        self.redraw_axis_names()

    @on_trait_change('lut_mode,colorbar')
    def on_change_lut_mode(self):
        self.view3d.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.view3d.module_manager.scalar_lut_manager.show_scalar_bar = self.colorbar
        self.ipw_x.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_y.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_z.module_manager.scalar_lut_manager.lut_mode = self.lut_mode

    def _on_change_index_4d(self, index_4d):
        index_3d = self._axis_map_4d_to_3d[index_4d]
        if index_3d:
            getattr(self, 'ipw_3d_{}'.format(index_3d)).ipw.slice_position = \
                getattr(self, '{}_index'.format(index_4d)) + 1
            self._set_data_value()
        else:
            ## sticky dim
            sel_indices = [self.ALL, self.ALL, self.ALL]
            sticky_index = getattr(self, '{}_index'.format(self._axis_4d[self._sticky_dim_index]))
            sel_indices.insert(self._sticky_dim_index, sticky_index)
            data = self.data[self.select_indices(*sel_indices)]
            data_range = data.min(), data.max()
            self.data_src3d.scalar_data = data
            self.view3d.module_manager.scalar_lut_manager.data_range = data_range
            self.ipw_x.module_manager.scalar_lut_manager.data_range = data_range
            self.ipw_y.module_manager.scalar_lut_manager.data_range = data_range
            self.ipw_z.module_manager.scalar_lut_manager.data_range = data_range
            self._set_data_value()

    @on_trait_change('w_index')
    def on_change_w_index(self):
        self._on_change_index_4d('w')
        
    @on_trait_change('x_index')
    def on_change_x_index(self):
        self._on_change_index_4d('x')
        
    @on_trait_change('y_index')
    def on_change_y_index(self):
        self._on_change_index_4d('y')
        
    @on_trait_change('z_index')
    def on_change_z_index(self):
        self._on_change_index_4d('z')
        
    #---------------------------------------------------------------------------
    # Scene activation callbaks
    #---------------------------------------------------------------------------
    @on_trait_change('scene3d.activated')
    def display_scene3d(self):
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
        self._set_data_value()
        self.on_change_lut_mode()


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
            self._set_data_value()

        ipw.ipw.add_observer('InteractionEvent', move_view)
        ipw.ipw.add_observer('StartInteractionEvent', move_view)

        # Center the image plane widget
        ipw.ipw.slice_position = getattr(self, '{}_index'.format(axis_name))

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
                '_',
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
                    'sticky_dim',
                    editor=EnumEditor(
                        values=['w', 'x', 'y', 'z']

                    ),
                    label="Sticky dimension",
                    enabled_when='is4D',
                    visible_when='is4D',
                    emphasized=True,
                    style="readonly",
                    tooltip="the sticky dimension",
                    help="4D volumes are sliced along the 'sticky dimension'; it is possible to change the value of this dimension using the related slider",
                ),
                Item(
                    '_',
                    enabled_when='is4D',
                    visible_when='is4D',
                ),
                Item(
                    'w_index',
                    editor=RangeEditor(
                        low_name='w_low',
                        high_name='w_high',
                        format="%d",
                        label_width=10,
                        mode="slider",
                    ),
                    enabled_when='is4D',
                    visible_when='is4D',
                    tooltip="the w dimension",
                ),
                Item(
                    'x_index',
                    editor=RangeEditor(
                        low_name='x_low',
                        high_name='x_high',
                        format="%d",
                        label_width=10,
                        mode="slider",
                    ),
                    format_str="%<8s",
                    tooltip="the x dimension",
                ),
                Item(
                    'y_index',
                    editor=RangeEditor(
                        low_name='y_low',
                        high_name='y_high',
                        format="%d",
                        label_width=10,
                        mode="slider",
                    ),
                    format_str="%<8s",
                    tooltip="the y dimension",
                ),
                Item(
                    'z_index',
                    editor=RangeEditor(
                        low_name='z_low',
                        high_name='z_high',
                        format="%d",
                        label_width=10,
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
                    emphasized=True,
                ),
                Item(
                    'lut_mode',
                    editor=EnumEditor(
                        values=COLORMAPS,

                    ),
                    label="Colormap",
                ),
                Item(
                    'colorbar',
                    editor=BooleanEditor(
                    ),
                    label="Colorbar",
                ),
                show_labels=True,
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
