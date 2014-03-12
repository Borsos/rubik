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

import numpy as np

from . import data_types
from .application import log

def extract(*, input_filename, output_filename, shape, selection, data_type=data_types.DEFAULT_DATA_TYPE):
    dtype = data_types.get_dtype(data_type)
    cube = np.fromfile(input_filename, dtype=data_type)
    cube = cube.reshape(shape.shape())
    log.LOGGER.info("extract: shape={0!r}".format(cube.shape))
    log.LOGGER.info("extract: picks={0!r}".format(selection, selection.picks()))
    subcube = cube[selection.picks()]
    subcube.tofile(output_filename)
