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
    'IntegerAttribute',
    'PositiveIntegerAttribute',
    'FloatAttribute',
    'FractionAttribute',
]

from .mayavi_data import COLORMAPS
from ..attribute import Attribute

class Colormap(Attribute):
    def __init__(self):
        default = 'blue-red'
        description = """\
Apply the selected colormap.
Available values: {values}
""".format(values=', '.join(repr(v) for v in COLORMAPS))
        super(Colormap, self).__init__(default=default, description=description)

    def convert(self, value):
        if not value in COLORMAPS:
            raise ValueError("invalid {} {!r}".format(self.__class__.__name__, value))
        return value

    def check_value(self, value):
        return value

    
class IntegerAttribute(Attribute):
    def convert(self, value):
        if isinstance(value, int):
            ivalue = value
        elif isinstance(value, basestring):
            try:
                ivalue = int(value)
            except ValueError:
                raise ValueError("invalid {}: {!r}: not an integer".format(self.__class__.__name__, value))
        else:
            raise ValueError("invalid {} {!r}".format(self.__class__.__name__, value))


class FloatAttribute(Attribute):
    def convert(self, value):
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        if isinstance(value, basestring):
            try:
                return float(value)
            except ValueError:
                raise ValueError("invalid {}: {!r}: not a float".format(self.__class__.__name__, value))
        raise ValueError("invalid {} {!r}".format(self.__class__.__name__, value))

class FractionAttribute(FloatAttribute):
    def check(self, value):
        if not (0.0 <= value <= 1.0):
            raise ValueError("invalid {} {!r}: not in [0.0, 1.0]".format(self.__class__.__name__, value))

class PositiveIntegerAttribute(IntegerAttribute):
    def check_value(self, value):
        if value <= 0:
            raise ValueError("invalid {} {!r}: not positive".format(self.__class__.__name__, value))
      
class BooleanAttribute(Attribute):
    def convert(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, basestring):
            if value.title() == "True":
                return True
            elif value.title() == "False":
                return False
        raise ValueError("invalid {} {!r}".format(self.__class__.__name__, value))


class Colorbar(BooleanAttribute):
    def __init__(self):
        default = False
        description = """\
Show the colorbar.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Colorbar, self).__init__(default=default, description=description)

class Transparent(BooleanAttribute):
    def __init__(self):
        default = False
        description = """\
Make IsoSurface transparent.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Transparent, self).__init__(default=default, description=description)

class Opacity(FloatAttribute):
    def __init__(self):
        default = 0.4
        description = """\
Set IsoSurface opacity.
Available values: 0.0 <= float <= 1.0
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Opacity, self).__init__(default=default, description=description)

class Contours(PositiveIntegerAttribute):
    def __init__(self):
        default = 5
        description = """\
Number of contours.
Available values: any positive integer
"""
        super(Contours, self).__init__(default=default, description=description)

