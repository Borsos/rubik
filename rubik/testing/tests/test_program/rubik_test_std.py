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
           'RubikTestStd',
          ]

from ....conf import VERSION
from ....shape import Shape

from ...rubik_test_program import RubikTestProgram
from ...rubik_test_case import testmethod

from ....cubes import api as cb

class RubikTestStd(RubikTestProgram):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestStd, self).setUp()
        self.X = 8
        self.Y = 10
        self.Z = 30
        self.XYZ = Shape((self.X, self.Y, self.Z))
        self.XY = Shape((self.X, self.Y))
        
        self.file_format = 'raw'

        self.filename_2d = {}
        self.filename_3d = {}
        for names, shape, filename_dict in (
                (('a', 'b', 'l'), self.XY, self.filename_2d),
                (('l', ), self.XYZ, self.filename_3d)
            ):
            for name in names:
                out_filename_format = "{n}_{{rank}}d_{{shape}}.{{format}}".format(n=name)
                out_filename = out_filename_format.format(n=name, rank=shape.rank(), shape=shape, format=self.file_format)
                filename_dict[name] = out_filename
                returncode, output, error = self.run_program(
                    """-e 'cb.linear_cube("{s}")' -o '{o}'""".format(
                        s=shape,
                        o=out_filename_format))
                self.assertEqual(returncode, 0)
                
    @testmethod
    def a_2d_exists(self):
        self.assertFileExistsAndHasShape(self.filename_2d['a'], self.XY)

    @testmethod
    def b_2d_exists(self):
        self.assertFileExistsAndHasShape(self.filename_2d['b'], self.XY)

    @testmethod
    def l_2d_exists(self):
        self.assertFileExistsAndHasShape(self.filename_2d['l'], self.XY)

    @testmethod
    def l_3d_exists(self):
        self.assertFileExistsAndHasShape(self.filename_3d['l'], self.XYZ)

    @testmethod
    def default_file_format(self):
        shape = self.XYZ
        file_format = self.file_format
        out_filename_format = "atmp0_{shape}.{format}"
        out_filename = out_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o '{o}'""".format(
                s=shape,
                o=out_filename_format))
        self.assertFileExistsAndHasShape(out_filename, shape)
        
    def impl_file_format(self, file_format):
        shape = self.XYZ
        out0_filename_format = "atmp0_{shape}.{format}"
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o '{o}' -Of {ff}""".format(
                s=shape,
                o=out0_filename_format,
                ff=file_format))
        self.assertFileExists(out0_filename)
        rfun = getattr(cb, 'read_cube_{}'.format(file_format))
        cube = rfun(out0_filename, shape=shape)
        self.assertTrue(cube.shape, shape.shape())
        out1_filename_format = "atmp1_{shape}.{format}"
        out1_filename = out1_filename_format.format(shape=shape, format='raw')
        returncode, output, error = self.run_program(
            """-i '{i}' -o '{o}' -s {s} -If {ff} -Of raw""".format(
                s=shape,
                i=out0_filename_format,
                o=out1_filename_format,
                ff=file_format))
        self.assertFileExistsAndHasShape(out1_filename, shape)
        self.assertFilesAreEqual(out1_filename, self.filename_3d['l'])

    @testmethod
    def raw_file_format(self):
        self.impl_file_format('raw')

    @testmethod
    def csv_file_format(self):
        self.impl_file_format('csv')

    @testmethod
    def text_file_format(self):
        self.impl_file_format('text')

    @testmethod
    def cube_6D(self):
        shape = Shape("6x10x5x9x4x12")
        out_filename_format = "ltmp_{rank}d_{shape}.{format}"
        out_filename = out_filename_format.format(shape=shape, format=self.file_format, rank=shape.rank())
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o '{o}'""".format(
                s=shape,
                o=out_filename_format))
        self.assertFileExistsAndHasShape(out_filename, shape)
