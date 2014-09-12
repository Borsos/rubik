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
           'RubikTestInfo',
          ]

from ....conf import VERSION
from ....shape import Shape
from ....cubes import api as cb

from ...rubik_test_program import RubikTestProgram
from ...rubik_test_case import testmethod

from ....cubes import api as cb

class RubikTestInfo(RubikTestProgram):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestInfo, self).setUp()
        self.X = 8
        self.Y = 10
        self.Z = 30
        self.XYZ = Shape((self.X, self.Y, self.Z))
        
        self.file_format = 'raw'

        self.filename_3d = {}
        for name_starts, shape, filename_dict in (
                ((('l0', 0), ('l1', 1), ('l2', 2)), self.XYZ, self.filename_3d),
            ):
            for name, start in name_starts:
                out_filename_format = "{n}_{{rank}}d_{{shape}}.{{format}}".format(n=name)
                out_filename = out_filename_format.format(n=name, rank=shape.rank(), shape=shape, format=self.file_format)
                filename_dict[name] = out_filename
                returncode, output, error = self.run_program(
                    """-e 'cb.linear_cube("{s}", start={S})' -o '{o}'""".format(
                        s=shape,
                        S=start,
                        o=out_filename_format))
                self.assertEqual(returncode, 0)
                
    @testmethod
    def l0_exists(self):
        self.assertFileExistsAndHasShape(self.filename_3d['l0'], self.XYZ)

    @testmethod
    def l1_exists(self):
        self.assertFileExistsAndHasShape(self.filename_3d['l1'], self.XYZ)

    @testmethod
    def l2_exists(self):
        self.assertFileExistsAndHasShape(self.filename_3d['l2'], self.XYZ)

    @testmethod
    def stats_3_files(self):
        shape = self.XYZ
        returncode, output, error = self.run_program(
            """-i '{l0}' -S -i '{l1}' -S -i '{l2}' -S -s '{s}' --verbose-level=10""".format(
                s=shape,
                l0=self.filename_3d['l0'],
                l1=self.filename_3d['l1'],
                l2=self.filename_3d['l2'],
        ))
        self.assertEqual(returncode, 0)
        self.assertEqual(output, """\
rubik: evaluating expression "read_cube(label='i0')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 0 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l0_3d_8x10x30.raw'...
rubik: evaluating expression 'print_stats()'...
rubik: executing 'eval' expression...
shape     = 8x10x30
#elements = 2400
%elements = 100.00%
min       = 0.0
min_index = (0, 0, 0)
max       = 2399.0
max_index = (7, 9, 29)
sum       = 2.8788e+06
ave       = 1199.5
#zero     = 1
%zero     = 0.04%
#nonzero  = 2399
%nonzero  = 99.96%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
rubik: evaluating expression "read_cube(label='i1')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 9600 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l1_3d_8x10x30.raw'...
rubik: evaluating expression 'print_stats()'...
rubik: executing 'eval' expression...
shape     = 8x10x30
#elements = 2400
%elements = 100.00%
min       = 1.0
min_index = (0, 0, 0)
max       = 2400.0
max_index = (7, 9, 29)
sum       = 2.8812e+06
ave       = 1200.5
#zero     = 0
%zero     = 0.00%
#nonzero  = 2400
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
rubik: evaluating expression "read_cube(label='i2')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 19200 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l2_3d_8x10x30.raw'...
rubik: evaluating expression 'print_stats()'...
rubik: executing 'eval' expression...
shape     = 8x10x30
#elements = 2400
%elements = 100.00%
min       = 2.0
min_index = (0, 0, 0)
max       = 2401.0
max_index = (7, 9, 29)
sum       = 2.8836e+06
ave       = 1201.5
#zero     = 0
%zero     = 0.00%
#nonzero  = 2400
%nonzero  = 100.00%
#nan      = 0
%nan      = 0.00%
#inf      = 0
%inf      = 0.00%
""")

    @testmethod
    def compare_3_files(self):
        shape = self.XYZ
        returncode, output, error = self.run_program(
            """-i '{l0}' -C -i '{l1}' -C -i '{l2}' -C -s '{s}' --verbose-level=10""".format(
                s=shape,
                l0=self.filename_3d['l0'],
                l1=self.filename_3d['l1'],
                l2=self.filename_3d['l2'],
        ))
        self.assertEqual(returncode, 0)
        self.assertEqual(output, """\
rubik: evaluating expression "read_cube(label='i0')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 0 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l0_3d_8x10x30.raw'...
rubik: evaluating expression 'compare_stats()'...
rubik: executing 'eval' expression...
rubik: evaluating expression "read_cube(label='i1')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 9600 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l1_3d_8x10x30.raw'...
rubik: evaluating expression 'compare_stats()'...
rubik: executing 'eval' expression...
rubik: evaluating expression "read_cube(label='i2')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 19200 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l2_3d_8x10x30.raw'...
rubik: evaluating expression 'compare_stats()'...
rubik: executing 'eval' expression...
shape     = 8x10x30    8x10x30    8x10x30
#elements = 2400       2400       2400
%elements = 100.00%    100.00%    100.00%
min       = 0.0        1.0        2.0
min_index = (0, 0, 0)  (0, 0, 0)  (0, 0, 0)
max       = 2399.0     2400.0     2401.0
max_index = (7, 9, 29) (7, 9, 29) (7, 9, 29)
sum       = 2.8788e+06 2.8812e+06 2.8836e+06
ave       = 1199.5     1200.5     1201.5
#zero     = 1          0          0
%zero     = 0.04%      0.00%      0.00%
#nonzero  = 2399       2400       2400
%nonzero  = 99.96%     100.00%    100.00%
#nan      = 0          0          0
%nan      = 0.00%      0.00%      0.00%
#inf      = 0          0          0
%inf      = 0.00%      0.00%      0.00%
""")

    @testmethod
    def diff_2_files(self):
        shape = self.XYZ
        returncode, output, error = self.run_program(
            """-i '{l0}' -D -i '{l1}' -D -s '{s}' --verbose-level=10""".format(
                s=shape,
                l0=self.filename_3d['l0'],
                l1=self.filename_3d['l1'],
        ))
        self.assertEqual(returncode, 0)
        self.assertEqual(output, """\
rubik: evaluating expression "read_cube(label='i0')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 0 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l0_3d_8x10x30.raw'...
rubik: evaluating expression 'diff()'...
rubik: executing 'eval' expression...
rubik: evaluating expression "read_cube(label='i1')"...
rubik: executing 'eval' expression...
rubik: trying to read 9600 bytes and extract 9600 bytes; already read 9600 bytes...
rubik: executing optimized read...
rubik: reading 2400 'float32' elements (9600 bytes) from 'raw' file 'l1_3d_8x10x30.raw'...
rubik: evaluating expression 'diff()'...
rubik: executing 'eval' expression...
name      = LEFT       RIGHT      REL_DIFF      ABS_DIFF
shape     = 8x10x30    8x10x30    8x10x30       8x10x30
#elements = 2400       2400       2400          2400
%elements = 100.00%    100.00%    100.00%       100.00%
min       = 0.0        1.0        0.00041684034 1.0
min_index = (0, 0, 0)  (0, 0, 0)  (7, 9, 29)    (0, 0, 0)
max       = 2399.0     2400.0     3.4028235e+38 1.0
max_index = (7, 9, 29) (7, 9, 29) (0, 0, 0)     (0, 0, 0)
sum       = 2.8788e+06 2.8812e+06 3.40282e+38   2400
ave       = 1199.5     1200.5     1.41784e+35   1
#zero     = 1          0          0             0
%zero     = 0.04%      0.00%      0.00%         0.00%
#nonzero  = 2399       2400       2400          2400
%nonzero  = 99.96%     100.00%    100.00%       100.00%
#nan      = 0          0          0             0
%nan      = 0.00%      0.00%      0.00%         0.00%
#inf      = 0          0          0             0
%inf      = 0.00%      0.00%      0.00%         0.00%
""")
