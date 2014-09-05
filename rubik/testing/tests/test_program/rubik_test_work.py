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
           'RubikTestWork',
          ]

from ....conf import VERSION
from ....shape import Shape

from ...rubik_test_program import RubikTestProgram
from ...rubik_test_case import testmethod

class RubikTestWork(RubikTestProgram):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestWork, self).setUp()
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

        self.file_format = 'raw'
        self.im_shape = self.XYZ
        self.og_shape = self.XYHZ
        self.c_shape = self.XYZ
        self.lin_shape = self.AB

        self.im_filename_format = 'im_{shape}.{format}'
        self.im_filename = self.im_filename_format.format(shape=self.im_shape, format=self.file_format)

        self.og_filename_format = 'im_{shape}.{format}'
        self.og_filename = self.og_filename_format.format(shape=self.og_shape, format=self.file_format)

        self.c_filename_format = 'c_{shape}.{format}'
        self.c_filename = self.c_filename_format.format(shape=self.c_shape, format=self.file_format)

        self.lin_filename_format = 'lin_{shape}.{format}'
        self.lin_filename = self.lin_filename_format.format(shape=self.lin_shape, format=self.file_format)

        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=self.im_shape,
                o=self.im_filename_format))

        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=self.og_shape,
                o=self.og_filename_format))

        returncode, output, error = self.run_program(
            """-e 'cb.const_cube("{s}", value={c})' -o '{o}'""".format(
                s=self.c_shape,
                c=self.CONST_VALUE,
                o=self.c_filename_format))

        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o '{o}'""".format(
                s=self.lin_shape,
                c=self.CONST_VALUE,
                o=self.lin_filename_format))

    @testmethod
    def im_exists(self):
        self.assertFileExistsAndHasShape(self.im_filename, self.im_shape)
        
    @testmethod
    def im_duplicate(self):
        out_filename_format = 'rtmp_{shape}.{format}'
        out_filename = out_filename_format.format(shape=self.im_shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o '{o}'""".format(
                s=self.im_shape,
                o=out_filename_format))
        self.assertFilesAreEqual(out_filename, self.im_filename)

    @testmethod
    def og_exists(self):
        self.assertFileExistsAndHasShape(self.og_filename, self.og_shape)

    @testmethod
    def og_slice(self):
        out_filename_format = 'og0_{shape}.{format}'
        out_filename = out_filename_format.format(shape=self.im_shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-i '{og}' -s '{s}' -x '{x}' -o '{o}'""".format(
                s=self.og_shape,
                x=":,:,{h},:".format(h=self.H//2),
                og=self.og_filename_format,
                o=out_filename_format))
        self.assertFileExistsAndHasShape(out_filename, self.im_shape)

    @testmethod
    def og_extract_and_split(self):
        out_filename_format = 'og_h{d2}_{shape}.{format}'
        hstart = 100
        hstop = 300
        hincr = 50
        extractor = ":,:,{hstart}:{hstop}:{hincr},:".format(
            hstart=hstart,
            hstop=hstop,
            hincr=hincr,
        )
        returncode, output, error = self.run_program(
            """-i '{og}' -s '{s}' -x '{x}' -o '{o}' --split 2""".format(
                s=self.og_shape,
                x=extractor,
                og=self.og_filename_format,
                o=out_filename_format))
        for d2, h in enumerate(range(hstart, hstop, hincr)):
            out_filename = out_filename_format.format(
                shape=self.im_shape,
                format=self.file_format,
                d2=d2,
            )
            self.assertFileExistsAndHasShape(out_filename, self.XYZ)

    @testmethod
    def const_cube_exists(self):
        self.assertFileExistsAndHasShape(self.c_filename, self.c_shape)

    @testmethod
    def const_cube_sum(self):
        returncode, output, error = self.run_program(
            """-i '{o}' -s {s} -e '_r.sum()' --print""".format(
                s=self.c_shape,
                c=self.CONST_VALUE,
                o=self.c_filename_format),
            join_stderr_stdout=False)
        self.assertEqual(output, "{}\n".format(self.c_shape.count() * self.CONST_VALUE))

    @testmethod
    def linear_cube_exists(self):
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

    @testmethod
    def ndarray(self):
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

    @testmethod
    def linear_cube_exists(self):
        self.assertFileExistsAndHasShape(self.lin_filename, self.lin_shape)

    @testmethod
    def equals_num(self):
        out_filename_format = 'l1_{shape}.{format}'
        out_filename = out_filename_format.format(shape=self.lin_shape, format=self.file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}", start=1.0, increment=2.0)' -o '{o}'""".format(
                s=self.lin_shape,
                c=self.CONST_VALUE,
                o=out_filename_format))
        self.assertFileExistsAndHasShape(out_filename, self.lin_shape)
        self.assertFilesDiffer(out_filename, self.lin_filename)

        for tolerance, result in (
                                  (0.0, 0),
                                  (1.0, min(1, self.lin_shape.count())),
                                  (10.0, min(10, self.lin_shape.count())),
                                  (1000.0, min(1000, self.lin_shape.count())),
                                 ):
            returncode, output, error = self.run_program(
                """-i '{l1}' -i '{l2}' -s {s} -e 'cb.equals_num(i0, i1, tolerance={t})' --print""".format(
                    s=self.lin_shape,
                    c=self.CONST_VALUE,
                    l1=self.lin_filename_format,
                    l2=out_filename_format,
                    t=tolerance),
                join_stderr_stdout=False)
            self.assertEqual(output, "{}\n".format(result))
