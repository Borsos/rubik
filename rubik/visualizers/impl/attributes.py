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
    'LOCATE_MODES',
    'LOCATE_MODE_MAX',
    'LOCATE_MODE_MIN',
    'LOCATE_MODE_VALUE',
    'LOCATE_MODE_DEFAULT',
    'ColormapAttribute',
    'ColorbarAttribute',
    'ContoursAttribute',
    'TransparentAttribute',
    'OpacityAttribute',
    'IndexAttribute',
    'Dimension4DAttribute',
    'ClipAttribute',
    'SymmetricClipAttribute',
    'LocateModeAttribute',
    'LocateValueAttribute',
]

LOCATE_MODE_MAX = 'max'
LOCATE_MODE_MIN = 'min'
LOCATE_MODE_VALUE = 'value'
LOCATE_MODES = [LOCATE_MODE_MAX, LOCATE_MODE_MIN, LOCATE_MODE_VALUE]
LOCATE_MODE_DEFAULT = LOCATE_MODES[0]

from .mayavi_data import COLORMAPS
from ..attribute_types import IntegerAttributeType, \
                              PositiveIntegerAttributeType, \
                              FloatAttributeType, \
                              FractionAttributeType, \
                              BooleanAttributeType, \
                              EnumAttributeType

from ..attribute import Attribute

class EnumAttribute(Attribute):
    def index(self, v):
        return self._attribute_type.index(v)

class ColormapAttribute(EnumAttribute):
    def __init__(self):
        default = 'blue-red'
        description = """\
Apply the selected colormap.
"""
        super(ColormapAttribute, self).__init__(default=default, description=description, attribute_type=EnumAttributeType(COLORMAPS))

class ColorbarAttribute(Attribute):
    def __init__(self):
        default = False
        description = """\
Show the colorbar.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(ColorbarAttribute, self).__init__(default=default, description=description, attribute_type=BooleanAttributeType())

class TransparentAttribute(Attribute):
    def __init__(self):
        default = False
        description = """\
Make IsoSurface transparent.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(TransparentAttribute, self).__init__(default=default, description=description, attribute_type=BooleanAttributeType())

class OpacityAttribute(Attribute):
    def __init__(self):
        default = 0.4
        description = """\
Set IsoSurface opacity.
Available values: 0.0 <= float <= 1.0
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(OpacityAttribute, self).__init__(default=default, description=description, attribute_type=FractionAttributeType())

class ContoursAttribute(Attribute):
    def __init__(self):
        default = 5
        description = """\
Number of contours.
Available values: any positive integer
"""
        super(ContoursAttribute, self).__init__(default=default, description=description, attribute_type=PositiveIntegerAttributeType())

class IndexAttribute(Attribute):
    def __init__(self, index_name):
        default = None
        self.index_name = index_name
        description = """\
{index_name} index for the initial slice.
Available values: any valid {index_name} index
""".format(index_name=self.index_name)
        super(IndexAttribute, self).__init__(default=default, description=description, attribute_type=PositiveIntegerAttributeType())

class Dimension4DAttribute(EnumAttribute):
    def __init__(self):
        self.dimensions = ['w', 'x', 'y', 'z']
        default = 'w'
        description = """\
4D dimension.
Available values: {values}
""".format(values=', '.join(repr(d) for d in self.dimensions))
        super(Dimension4DAttribute, self).__init__(default=default, description=description, attribute_type=EnumAttributeType(self.dimensions))

class ClipAttribute(Attribute):
    def __init__(self):
        default = None
        description = """\
Clip value
Available values: any float
"""
        super(ClipAttribute, self).__init__(default=default, description=description, attribute_type=FloatAttributeType())

class SymmetricClipAttribute(Attribute):
    def __init__(self):
        default = False
        description = """\
Set symmetric clip.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(SymmetricClipAttribute, self).__init__(default=default, description=description, attribute_type=BooleanAttributeType())

class LocateModeAttribute(EnumAttribute):
    def __init__(self):
        default = None
        description = """\
Locate mode: {}
""".format('|'.join(e for e in LOCATE_MODES))
        super(LocateModeAttribute, self).__init__(default=default, description=description, attribute_type=EnumAttributeType(LOCATE_MODES))

class LocateValueAttribute(Attribute):
    def __init__(self):
        default = None
        description = """\
Locate value
"""
        super(LocateValueAttribute, self).__init__(default=default, description=description, attribute_type=FloatAttributeType())
