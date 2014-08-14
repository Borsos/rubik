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
    'colormap',
    'colorbar',
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

    def validate(self, value):
        if not value in COLORMAPS:
            raise ValueError("invalid colormap {!r}".format(value))
        return value

class Colorbar(Attribute):
    def __init__(self):
        default = False
        description = """\
Show the colorbar.
Available values: {values}
""".format(values=', '.join(repr(v) for v in (True, False)))
        super(Colorbar, self).__init__(default=default, description=description)

    def validate(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, basestring):
            if value.title() == "True":
                return True
            elif value.title() == "False":
                return False
        raise ValueError("invalid colormap {!r}".format(value))
