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

import numpy as np

from traits.api import HasTraits, Instance, Array, \
    Float, Str, Range, Enum, \
    on_trait_change
from traitsui.api import View, Item, HGroup, Group, \
    Label, RangeEditor, EnumEditor

from tvtk.api import tvtk
from tvtk.pyface.scene import Scene

from mayavi import mlab
from mayavi.core.api import PipelineBase, Source
from mayavi.core.ui.api import SceneEditor, MayaviScene, \
                                MlabSceneModel

from .mayavi_data import COLORMAPS
from .attributes import Colormap
from ..base_viewer import BaseViewer

################################################################################
# The object implementing the dialog
class VolumeSlicer(HasTraits, BaseViewer):
    ATTRIBUTES = {
        'colormap': Colormap(),
    }
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
    x_low = Float
    x_high = Float
    x_index = Float
    x_range = Range(low='x_low', high='x_high', value='x_index')
    y_low = Float(0.0)
    y_high = Float(0.0)
    y_index = Float(0.0)
    y_range = Range(low='y_low', high='y_high', value='y_index')
    z_low = Float(0.0)
    z_high = Float(0.0)
    z_index = Float(0.0)
    z_range = Range(low='z_low', high='z_high', value='z_index')
    data_value = Str("")

    lut_mode = Enum(*COLORMAPS)

    _axis_names = dict(x=0, y=1, z=2)


    #---------------------------------------------------------------------------
    def __init__(self, **traits):
        super(VolumeSlicer, self).__init__(**traits)
        BaseViewer.__init__(self)
        # Force the creation of the image_plane_widgets:
        self.ipw_3d_x
        self.ipw_3d_y
        self.ipw_3d_z
        self.x_low, self.y_low, self.z_low = 0, 0, 0
        self.x_high, self.y_high, self.z_high = self.data.shape

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

    def _lut_mode_default(self):
        return self.attributes["colormap"]

    def _x_index_default(self):
        return self.x_high // 2

    def _y_index_default(self):
        return self.y_high // 2

    def _z_index_default(self):
        return self.z_high // 2

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
        self.data_value = str(self.data[self.x_index, self.y_index, self.z_index])

    @on_trait_change('lut_mode')
    def change_lut_mode(self):
        self.view3d.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_x.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_y.module_manager.scalar_lut_manager.lut_mode = self.lut_mode
        self.ipw_z.module_manager.scalar_lut_manager.lut_mode = self.lut_mode

    @on_trait_change('x_index')
    def change_x_index(self):
        self.ipw_3d_x.ipw.slice_position = self.x_index
        self._set_data_value()
        
    @on_trait_change('y_index')
    def change_y_index(self):
        self.ipw_3d_y.ipw.slice_position = self.y_index
        self._set_data_value()
        
    @on_trait_change('z_index')
    def change_z_index(self):
        self.ipw_3d_z.ipw.slice_position = self.z_index
        self._set_data_value()
        

    #---------------------------------------------------------------------------
    # Scene activation callbaks
    #---------------------------------------------------------------------------
    @on_trait_change('scene3d.activated') #,x_index,y_index,z_index')
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
        self.change_lut_mode()


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
            for other_axis, axis_number in self._axis_names.iteritems():
                if other_axis == axis_name:
                    continue
                ipw3d = getattr(self, 'ipw_3d_%s' % other_axis)
                ipw3d.ipw.slice_position = position[axis_number]
                axis_index_name = "{}_index".format(other_axis)
                setattr(self, axis_index_name, position[axis_number])
            self.data_value = str(self.data[position])

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
        mlab.text(0.01, 0.9, axis_name, width=0.04)



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
                    height=250, width=300
                ),
                Item('scene_z',
                    editor=SceneEditor(scene_class=Scene),
                    height=250, width=300
                ),
                show_labels=False,
            ),
            Group(
                Item('scene_x',
                    editor=SceneEditor(scene_class=Scene),
                    height=250, width=300
                ),
                Item('scene3d',
                    editor=SceneEditor(scene_class=MayaviScene),
                    height=250, width=300
                ),
                show_labels=False,
            ),
            Group(
                '_',
                Item(
                    'x_index',
                    editor=RangeEditor(
                        low_name='x_low',
                        high_name='x_high',
                        format="%.0f",
                        label_width=10,
                        mode="auto",
                    ),
                    format_str="%<8s",
                ),
                Item(
                    'y_index',
                    editor=RangeEditor(
                        low_name='y_low',
                        high_name='y_high',
                        format="%.0f",
                        label_width=10,
                        mode="auto",
                    ),
                ),
                Item(
                    'z_index',
                    editor=RangeEditor(
                        low_name='z_low',
                        high_name='z_high',
                        format="%.0f",
                        label_width=10,
                        mode="auto",
                    ),
                ),
                Item(
                    'data_value',
                    label="Value",
                    style="readonly",
                ),
                Item(
                    'lut_mode',
                    editor=EnumEditor(
                        values=COLORMAPS,

                    ),
                    label="Colormap",
                ),
                show_labels=True,
            ),
        ),
        resizable=True,
        title='Volume Slicer',
    )


if __name__ == "__main__":
    ################################################################################
    # Create some data
    x, y, z = np.ogrid[-5:5:64j, -5:5:64j, -5:5:64j]
    data = np.sin(3*x)/x + 0.05*z**2 + np.cos(3*y)
    
    m = VolumeSlicer(data=data)
    m.configure_traits()
