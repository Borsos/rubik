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
           'RubikTestProgramWork',
          ]

import subprocess

from ....conf import VERSION
from ....shape import Shape

from ...rubik_test_program import RubikTestProgram

class RubikTestProgramWork(RubikTestProgram):
    def setUp(self):
        super(RubikTestProgramWork, self).setUp()
        self.X = 10
        self.Y = 20
        self.Z = 30
        self.H = 501
        self.XYZ = Shape((self.X, self.Y, self.Z))
        self.HXYZ = Shape((self.H, self.X, self.Y, self.Z))
        self.XYHZ = Shape((self.X, self.Y, self.H, self.Z))
        
        self.A = 8
        self.B = 10
        self.AB = Shape((self.A, self.B))

        self.CONST_VALUE = 7.0

    def runTest_ProgramWorkRandomXYZCube(self):
        shape = self.XYZ
        file_format = 'raw'
        out0_filename_format = 'im_{shape}.{format}'
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=shape,
                o=out0_filename_format))
        self.assertFileExistsAndHasShape(out0_filename, shape)

        out1_filename_format = 'rtmp_{shape}.{format}'
        out1_filename = out1_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=shape,
                o=out1_filename_format))
        self.assertFilesAreEqual(out1_filename, out0_filename)

    def runTest_ProgramWorkRandomXYHZCube(self):
        shape = self.XYHZ
        file_format = 'raw'
        out0_filename_format = 'og_{shape}.{format}'
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=shape,
                o=out0_filename_format))
        self.assertFileExistsAndHasShape(out0_filename, shape)

        out1_filename_format = 'og0_{shape}.{format}'
        out1_filename = out1_filename_format.format(shape=self.XYZ, format=file_format)
        returncode, output, error = self.run_program(
            """-i '{o0}' -s '{s}' -x '{x}' -o '{o1}'""".format(
                s=shape,
                x=":,:,{h},:".format(h=self.H//2),
                o0=out0_filename_format,
                o1=out1_filename_format))
        self.assertFileExistsAndHasShape(out1_filename, self.XYZ)

        out2_filename_format = 'og_h{d2}_{shape}.{format}'
        hstart = 100
        hstop = 300
        hincr = 50
        returncode, output, error = self.run_program(
            """-i '{o0}' -s '{s}' -x '{x}' -o '{o2}' --split 2""".format(
                s=shape,
                x=":,:,{hstart}:{hstop}:{hincr},:".format(
                    hstart=hstart,
                    hstop=hstop,
                    hincr=hincr,
                ),
                o0=out0_filename_format,
                o2=out2_filename_format))
        for d2, h in enumerate(range(hstart, hstop, hincr)):
            out2_filename = out2_filename_format.format(
                shape=self.XYZ,
                format=file_format,
                d2=d2,
            )
            self.assertFileExistsAndHasShape(out2_filename, self.XYZ)

    def runTest_ProgramWorkConstCube(self):
        shape = self.XYZ
        file_format = 'raw'
        out0_filename_format = 'c_{shape}.{format}'
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.const_cube("{s}", value={c})' -o '{o}'""".format(
                s=shape,
                c=self.CONST_VALUE,
                o=out0_filename_format))
        self.assertFileExistsAndHasShape(out0_filename, shape)

        returncode, output, error = self.run_program(
            """-i '{o}' -s {s} -e '_r.sum()' --print""".format(
                s=shape,
                c=self.CONST_VALUE,
                o=out0_filename_format),
            stderr=subprocess.PIPE)
        self.assertEqual(output, "{}\n".format(shape.count() * self.CONST_VALUE))

    def runTest_ProgramWorkLinearCube(self):
        shape = self.XYZ
        file_format = 'raw'
        out0_filename_format = 'l_{shape}.{format}'
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}", start=2.0)' -o '{o}'""".format(
                s=shape,
                c=self.CONST_VALUE,
                o=out0_filename_format))
        self.assertFileExistsAndHasShape(out0_filename, shape)

    def runTest_ProgramWorkNdArray(self):
        shape = self.XYZ
        file_format = 'raw'
        out0_filename_format = 'nd_{shape}.{format}'
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'np.array([[[k for z in range({Z})] for j in range({Y})] for k in range({X})])' -o '{o}'""".format(
                X=self.X,
                Y=self.Y,
                Z=self.Z,
                o=out0_filename_format))
        self.assertFileExistsAndHasShape(out0_filename, shape)

    def runTest_ProgramWorkEquals(self):
        shape = self.AB
        file_format = 'raw'
        out0_filename_format = 'l0_{shape}.{format}'
        out0_filename = out0_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o '{o}'""".format(
                s=shape,
                c=self.CONST_VALUE,
                o=out0_filename_format))
        self.assertFileExistsAndHasShape(out0_filename, shape)

        out1_filename_format = 'l1_{shape}.{format}'
        out1_filename = out1_filename_format.format(shape=shape, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}", start=1.0, increment=2.0)' -o '{o}'""".format(
                s=shape,
                c=self.CONST_VALUE,
                o=out1_filename_format))
        self.assertFileExistsAndHasShape(out1_filename, shape)
        self.assertFilesDiffer(out1_filename, out0_filename)

        for tolerance, result in (
                                  (0.0, 0),
                                  (1.0, min(1, shape.count())),
                                  (10.0, min(10, shape.count())),
                                  (1000.0, min(1000, shape.count())),
                                 ):
            returncode, output, error = self.run_program(
                """-i '{o0}' -i '{o1}' -s {s} -e 'cb.equals_num(i0, i1, tolerance={t})' --print""".format(
                    s=shape,
                    c=self.CONST_VALUE,
                    o0=out0_filename_format,
                    o1=out1_filename_format,
                    t=tolerance),
                stderr=subprocess.PIPE)
            self.assertEqual(output, "{}\n".format(result))