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
    'Colormap',
    'Colorbar',
    'Contours',
    'Transparent',
    'Opacity',
    'Index',
]

from .mayavi_data import COLORMAPS
from ..attribute import Attribute, Integer, PositiveInteger, Float, Fraction, Boolean, Enum

class Colormap(Attribute):
    def __init__(self):
        default = 'blue-red'
        description = """\
Apply the selected colormap.
"""
        super(Colormap, self).__init__(default=default, description=description, attribute_type=Enum(COLORMAPS))

    def index(self, v):
        return self._attribute_type.index(v)

class Colorbar(Attribute):
    def __init__(self):
        default = False
        description = """\
Show the colorbar.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Colorbar, self).__init__(default=default, description=description, attribute_type=Boolean())

class Transparent(Attribute):
    def __init__(self):
        default = False
        description = """\
Make IsoSurface transparent.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Transparent, self).__init__(default=default, description=description, attribute_type=Boolean())

class Opacity(Attribute):
    def __init__(self):
        default = 0.4
        description = """\
Set IsoSurface opacity.
Available values: 0.0 <= float <= 1.0
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Opacity, self).__init__(default=default, description=description, attribute_type=Fraction())

class Contours(Attribute):
    def __init__(self):
        default = 5
        description = """\
Number of contours.
Available values: any positive integer
"""
        super(Contours, self).__init__(default=default, description=description, attribute_type=PositiveInteger())

class Index(Attribute):
    def __init__(self, index_name):
        default = None
        self.index_name = index_name
        description = """\
{index_name} index for the initial slice.
Available values: any valid {index_name} index
""".format(index_name=self.index_name)
        super(Index, self).__init__(default=default, description=description, attribute_type=PositiveInteger())

class Dimension4D(Attribute):
    def __init__(self):
        self.dimensions = ['w', 'x', 'y', 'z']
        default = 'w'
        description = """\
4D dimension.
Available values: {values}
""".format(values=', '.join(repr(d) for d in self.dimensions))
        super(Dimension4D, self).__init__(default=default, description=description, attribute_type=Enum(self.dimensions))

    def index(self, v):
        return self._attribute_type.index(v)
