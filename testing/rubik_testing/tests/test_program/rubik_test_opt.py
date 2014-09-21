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
           'RubikTestConfig',
          ]

import os

from rubik.shape import Shape
from rubik.extractor import Extractor
from rubik.units import Memory
from rubik.cubes import api as cb

from ...rubik_test_program import RubikTestProgram
from ...rubik_test_case import testmethod

class RubikTestOpt(RubikTestProgram):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestOpt, self).setUp()

    def impl_read(self, shape, extractor, dtype, threshold_size):
        shape = Shape(shape)
        extractor = Extractor(extractor)
        threshold_size = Memory(threshold_size)
        dtype = cb.get_dtype(dtype)
        file_format = 'raw'
        out_filename_format = 'xtmp_{shape}_{dtype}.{format}'
        out_filename = out_filename_format.format(shape=shape, dtype=dtype.__name__, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=shape,
                o=out_filename_format))
        self.assertEqual(returncode, 0)
        self.assertFileExistsAndHasShape(out_filename, shape=shape, dtype=dtype)

        out1_filename_format = 'xtmp1_{shape}_{dtype}.{format}'
        out1_filename = out1_filename_format.format(shape=shape, dtype=dtype.__name__, format=file_format)
        returncode, output, error = self.run_program(
            """-i '{o}' -s {s} -x '{x}' --read-threshold-size=0 -o {o1}""".format(
                s=shape,
                x=extractor,
                o=out_filename_format,
                o1=out1_filename_format))
        self.assertEqual(returncode, 0)

        out2_filename_format = 'xtmp2_{shape}_{dtype}.{format}'
        out2_filename = out2_filename_format.format(shape=shape, dtype=dtype.__name__, format=file_format)
        returncode, output, error = self.run_program(
            """-i '{o}' -s {s} -x '{x}' --read-threshold-size={ms} -o {o2}""".format(
                s=shape,
                x=extractor,
                o=out_filename_format,
                o2=out2_filename_format,
                ms=threshold_size))
        self.assertEqual(returncode, 0)

    @testmethod
    def random_4x5x6_float32_1g(self):
        self.impl_read(shape="4x5x6", extractor="1:,::2,:-1", dtype="float32", threshold_size="1g")

    @testmethod
    def random_4x5x6_float32_13b(self):
        self.impl_read(shape="4x5x6", extractor="1:,::2,:-1", dtype="float32", threshold_size="13b")

    @testmethod
    def random_4x5x6_float32_1k(self):
        self.impl_read(shape="4x5x6", extractor="1:,::2,:-1", dtype="float32", threshold_size="1k")

    @testmethod
    def random_40x50x60x8_float32_1g(self):
        self.impl_read(shape="40x50x60x8", extractor="::2,:,:,:", dtype="float32", threshold_size="1g")

    @testmethod
    def random_40x50x60x8_float32_13b(self):
        self.impl_read(shape="40x50x60x8", extractor="::2,:,:,:", dtype="float32", threshold_size="13b")

    @testmethod
    def random_40x50x60x8_float32_1k(self):
        self.impl_read(shape="40x50x60x8", extractor="::2,:,:,:", dtype="float32", threshold_size="1k")
