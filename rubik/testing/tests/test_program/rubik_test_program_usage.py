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
           'RubikTestProgramUsage',
          ]

import numpy as np
import subprocess

from ....conf import VERSION
from ....shape import Shape

from ...rubik_test_program import RubikTestProgram

class RubikTestProgramUsage(RubikTestProgram):
    def setUp(self):
        super(RubikTestProgramUsage, self).setUp()
        self.X = 8
        self.Y = 10
        self.Z = 20
        self.XYZ = Shape((self.X, self.Y, self.Z))

        self.shape = self.XYZ
        self.file_format = 'raw'

        # create random cube:
        self.r_filename_format = 'r_{shape}.{format}'
        self.r_filename = self.r_filename_format.format(shape=self.shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=self.shape,
                o=self.r_filename_format))
        
        # create linear cube:
        self.l_filename_format = 'l_{shape}.{format}'
        self.l_filename = self.l_filename_format.format(shape=self.shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o '{o}'""".format(
                s=self.shape,
                o=self.l_filename_format))

    def runTest_ProgramUsageRandomCube(self):
        self.assertFileExistsAndHasShape(self.r_filename, self.shape)

    def runTest_ProgramUsageLinearCube(self):
        self.assertFileExistsAndHasShape(self.l_filename, self.shape)

    def runTest_ProgramUsageWriteAndReadText(self):
        out1_filename_format = 'rtmp1_{shape}.{format}'
        out1_filename = out1_filename_format.format(shape=self.shape, format='text')
        returncode, output, error = self.run_program(
            """-i '{r}' -s '{s}' -o '{o1}' -Of text""".format(
                s=self.shape,
                r=self.r_filename_format,
                o1=out1_filename_format))
        self.assertFileExists(out1_filename)

        out2_filename_format = 'rtmp2_{shape}.{format}'
        out2_filename = out2_filename_format.format(shape=self.shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-i '{o1}' -s '{s}' -o '{o2}' -If text""".format(
                s=self.shape,
                o2=out2_filename_format,
                o1=out1_filename_format))
        self.assertFilesAreEqual(out2_filename, self.r_filename)

    def runTest_ProgramUsageWriteFloat64(self):
        out_filename_format = 'rtmp3_{shape}.{format}'
        out_filename = out_filename_format.format(shape=self.shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-i '{r}' -s '{s}' -o '{o}' -Ot float64""".format(
                s=self.shape,
                r=self.r_filename_format,
                o=out_filename_format))
        self.assertFileExistsAndHasShape(out_filename, self.shape, dtype=np.float64)

    def runTest_ProgramUsageExtractor(self):
        for extractor, sub_shape in (
            (":,2:-2,:",	Shape((self.X, max(0, self.Y - 4), self.Z))),
            (":,::2,::4",	Shape((self.X, (self.Y // 2), (self.Z // 4)))),
            (":,5,:",	Shape((self.X, self.Z))),
            (":,::2,:",	Shape((self.X, (self.Y // 2), self.Z))),
        ):
            out_filename_format = 'rtmp4_{shape}.{format}'
            out_filename = out_filename_format.format(shape=sub_shape, format=self.file_format)
            returncode, output, error = self.run_program(
                """-i '{r}' -s '{s}' -o '{o}' -x '{x}'""".format(
                    s=self.shape,
                    x=extractor,
                    r=self.r_filename_format,
                    o=out_filename_format))
            self.assertFileExistsAndHasShape(out_filename, sub_shape)
 
    def runTest_ProgramUsageSplit(self):
        out_filename_format = 'rtmp5_y{d1}_{shape}.{format}'
        yincr = 2
        extractor = ":,::{},:".format(yincr)
        returncode, output, error = self.run_program(
            """-i '{r}' -s '{s}' -o '{o}' -x '{x}' --split 1""".format(
                s=self.shape,
                x=extractor,
                r=self.r_filename_format,
                o=out_filename_format))
        sub_shape = Shape((self.X, self.Z))
        for d1, y in enumerate(range(0, self.Y, yincr)):
            out_filename = out_filename_format.format(shape=sub_shape, format=self.file_format, d1=d1)
            self.assertFileExistsAndHasShape(out_filename, sub_shape)

        
    def runTest_ProgramUsageExpression(self):
        out_filename_format = 'r6_{shape}.{format}'
        out_filename = out_filename_format.format(shape=self.shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-i '{r}' -i '{l}' -s '{s}' -e '0.5 * i0 - i1 / 0.5' -o '{o}' -Ot float64""".format(
                s=self.shape,
                r=self.r_filename_format,
                l=self.l_filename_format,
                o=out_filename_format))
        self.assertFileExistsAndHasShape(out_filename, self.shape, dtype=np.float64)

