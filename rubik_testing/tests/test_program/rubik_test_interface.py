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
           'RubikTestInterface',
          ]

import os

import numpy as np

from rubik.conf import VERSION
from rubik.shape import Shape
from rubik.application import logo
from rubik.cubes import api as cb

from ...rubik_test_case import testmethod
from ...rubik_test_program import RubikTestProgram

class RubikTestInterface(RubikTestProgram):
    METHOD_NAMES = []

    @testmethod
    def help(self):
        returncode, output, error = self.run_program("--help")
        self.assertEqual(returncode, 0)

    @testmethod
    def usage(self):
        returncode, output, error = self.run_program("--usage")
        self.assertEqual(returncode, 0)

    @testmethod
    def logo(self):
        returncode, output, error = self.run_program("--logo")
        self.assertEqual(returncode, 0)
        self.assertEqual(output, "{}\n".format(logo.RUBIK))

    @testmethod
    def version(self):
        returncode, output, error = self.run_program("--version")
        self.assertEqual(returncode, 0)
        self.assertEqual(output, "rubik {}\n".format(VERSION))

    @testmethod
    def dry_run(self):
        returncode, output, error = self.run_program("-i non_existent.tmp1 -s 4x6 -o non_existent.tmp2 --dry-run")
        self.assertEqual(returncode, 0)

    @testmethod
    def report_dry_run(self):
        returncode, output, error = self.run_program("-i non_existent.tmp1 -s 4x6 -o non_existent.tmp2 --dry-run --report")
        self.assertEqual(returncode, 0)

    @testmethod
    def histogram_number(self):
        returncode, output, error = self.run_program("-e 'cb.random_cube((4, 5))' --histogram")
        self.assertEqual(returncode, 0)

    @testmethod
    def histogram_percentage(self):
        returncode, output, error = self.run_program("-e 'cb.random_cube((4, 5))' --histogram --histogram-percentage")
        self.assertEqual(returncode, 0)

    @testmethod
    def histogram_bins_8(self):
        returncode, output, error = self.run_program("-e 'cb.random_cube((4, 5))' --histogram --histogram-bins=8 --histogram-range 0.1 0.9")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_expression(self):
        returncode, output, error = self.run_program("--help-expression")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_extractor(self):
        returncode, output, error = self.run_program("--help-extractor")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_user_defined_variables(self):
        returncode, output, error = self.run_program("--help-user-defined-variables")
        self.assertEqual(returncode, 0)

#    @testmethod
#    def help_numpy(self):
#        returncode, output, error = self.run_program("--help-numpy")
#        self.assertEqual(returncode, 0)
#
#    @testmethod
#    def help_cubes(self):
#        returncode, output, error = self.run_program("--help-cubes")
#        self.assertEqual(returncode, 0)

    @testmethod
    def help_filenames(self):
        returncode, output, error = self.run_program("--help-filenames")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_split(self):
        returncode, output, error = self.run_program("--help-split")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_environment_variables(self):
        returncode, output, error = self.run_program("--help-environment-variables")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_creating_cubes(self):
        returncode, output, error = self.run_program("--help-creating-cubes")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_output(self):
        returncode, output, error = self.run_program("--help-output")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_memory_usage(self):
        returncode, output, error = self.run_program("--help-memory-usage")
        self.assertEqual(returncode, 0)

    @testmethod
    def help_usage(self):
        returncode, output, error = self.run_program("--help-usage")
        self.assertEqual(returncode, 0)

    # labeled options
    def impl_labeled_options(self, shape, dtype, i0_label=None, i1_label=None, i2_label=None, o0_label=None, o1_label=None):
        shape = Shape(shape)
        dtype = cb.get_dtype(dtype)
        file_format = 'raw'

        i0_label_definition = ''
        i1_label_definition = ''
        i2_label_definition = ''
        o0_label_definition = ''
        o1_label_definition = ''
        if i0_label is None:
            i0_label = 'i0'
        else:
            i0_label_definition = '{}='.format(i0_label)
        if i1_label is None:
            i1_label = 'i1'
        else:
            i1_label_definition = '{}='.format(i1_label)
        if i2_label is None:
            i2_label = 'i2'
        else:
            i2_label_definition = '{}='.format(i2_label)
        if o0_label is None:
            o0_label = 'o0'
        else:
            o0_label_definition = '{}='.format(o0_label)
        if o1_label is None:
            o1_label = 'o1'
        else:
            o1_label_definition = '{}='.format(o1_label)


        lc_filename_format = "lcube_{shape}_{dtype}.{format}"
        lc_filename = lc_filename_format.format(shape=shape, dtype=dtype.__name__, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.linear_cube("{s}")' -o {lc}""".format(
                s=shape,
                lc=lc_filename_format,
            )
        )
        self.assertEqual(returncode, 0)
        self.assertFileExistsAndHasShape(lc_filename, shape=shape, dtype=dtype)

        rc_shape = Shape("100x{}".format(shape))
        rc_extractor = "3," + ','.join(':' for d in shape)
        rc_filename_format = "rcube_{shape}_{dtype}.{format}"
        rc_filename = rc_filename_format.format(shape=rc_shape, dtype=dtype.__name__, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.random_cube("{s}")' -o {rc}""".format(
                s=rc_shape,
                rc=rc_filename_format,
            )
        )
        self.assertEqual(returncode, 0)

        cc_filename_format = "ccube_{shape}_{dtype}.{format}"
        cc_filename = cc_filename_format.format(shape=shape, dtype=dtype.__name__, format=file_format)
        returncode, output, error = self.run_program(
            """-e 'cb.const_cube("{s}", value=0.2)' -o {cc}""".format(
                s=shape,
                cc=cc_filename_format,
            )
        )
        self.assertEqual(returncode, 0)
        self.assertFileExistsAndHasShape(cc_filename, shape=shape, dtype=dtype)
        
        o0_filename_format = "o0cube_{shape}_{dtype}.{format}"
        o0_file_format = 'text'
        o0_filename = o0_filename_format.format(shape=shape, dtype=dtype.__name__, format=o0_file_format)

        o1_filename_format = "o1cube_{shape}_{dtype}.{format}"
        o1_file_format = 'csv'
        o1_filename = o1_filename_format.format(shape=shape, dtype=dtype.__name__, format=o1_file_format)
        command = """-i '{i0ld}{lc}' -i '{i1ld}{rc}' -i '{i2ld}{cc}' -s '{s}' -s '{i1l}={rs}' -x '{i1l}={rcx}' -e '{i0l} + {i1l}' -o '{o0ld}{o0}' -e '{i0l} - {i1l}' -o '{o1ld}{o1}' -Of '{o0l}={o0f}' -Of '{o1l}={o1f}'""".format(
            s=shape,
            rs=rc_shape,
            lc=lc_filename_format,
            rc=rc_filename_format,
            cc=cc_filename_format,
            o0=o0_filename_format,
            o0f=o0_file_format,
            o1=o1_filename_format,
            o1f=o1_file_format,
            rcx=rc_extractor,
            i0l=i0_label,
            i1l=i1_label,
            i2l=i2_label,
            o0l=o0_label,
            o1l=o1_label,
            i0ld=i0_label_definition,
            i1ld=i1_label_definition,
            i2ld=i2_label_definition,
            o0ld=o0_label_definition,
            o1ld=o1_label_definition,
        )
        returncode, output, error = self.run_program(command)
        self.assertEqual(returncode, 0)
        self.assertFileExists(o0_filename)
        self.assertFileExists(o1_filename)
        self.remove_files(rc_filename, lc_filename, cc_filename, o0_filename, o1_filename)

    @testmethod
    def labeled_options_4x5_float32(self, shape="4x5", dtype="float32"):
        self.impl_labeled_options(shape=shape, dtype=dtype)

    @testmethod
    def labeled_options_4x5_float32_l_r_c_x_y(self, shape="4x5", dtype="float32"):
        self.impl_labeled_options(shape=shape, dtype=dtype, i0_label='l', i1_label='r', i2_label='c', o0_label='x', o1_label='y')

    def impl_expression_filename(self, shape, dtype, mode):
        shape = Shape(shape)
        dtype = cb.get_dtype(dtype)
        file_format = 'raw'

        out_filename_format = "outcube_{mode}_{{shape}}_{{dtype}}.{{format}}".format(mode=mode)
        out_filename = out_filename_format.format(shape=shape, dtype=dtype.__name__, format=file_format)
        expr_filename = "expr_{mode}.txt".format(mode=mode)
        with open(expr_filename, "w") as f_out:
            f_out.write("""\
cube = cb.linear_cube(shape="{s}", dtype="{d}")
cb.write_cube(file_format="{f}", cube=cube, file="{o}")
""".format(s=shape, d=dtype.__name__, o=out_filename_format, f=file_format))
        if mode == "f_option":
            command = "-f {e}".format(e=expr_filename)
        else:
            command = "-e '@{e}'".format(e=expr_filename)
        returncode, output, error = self.run_program(command)
        self.assertEqual(returncode, 0)
        self.assertFileExistsAndHasShape(out_filename, shape=shape, dtype=dtype)
        

    @testmethod
    def expression_filename_4x5_float32_f_option(self):
        self.impl_expression_filename(shape="4x5", dtype="float64", mode="f_option")

    @testmethod
    def expression_filename_8x3x2_float32_f_option(self):
        self.impl_expression_filename(shape="8x3x2", dtype="float64", mode="f_option")

    @testmethod
    def expression_filename_4x5_float32_at_option(self):
        self.impl_expression_filename(shape="4x5", dtype="float64", mode="at_option")

    @testmethod
    def expression_filename_8x3x2_float32_at_option(self):
        self.impl_expression_filename(shape="8x3x2", dtype="float64", mode="at_option")

    # view attributes
    def impl_view_attribute(self, attribute_name, attribute_value):
        returncode, output, error = self.run_program("--view-attribute {}={!r}".format(attribute_name, attribute_value))
        self.assertEqual(returncode, 0)
        
    @testmethod
    def view_attribute_clip_symmetric(self):
        self.impl_view_attribute("clip_symmetric", "True")
        
    @testmethod
    def view_attribute_x(self):
        self.impl_view_attribute("x", "0.33")

    # view attribute files
    def impl_view_attributes(self, **attribute_dict):
        filename = "view_attributes.txt"
        try:
            with open(filename, "w") as f_out:
                for attribute_name, attribute_value in attribute_dict.items():
                    f_out.write("{}={!r}\n".format(attribute_name, attribute_value))
            returncode, output, error = self.run_program("--view-attribute-file {}".format(filename))
            self.assertEqual(returncode, 0)
        finally:
            os.remove(filename)
        
    @testmethod
    def view_attribute_file(self):
        self.impl_view_attributes(clip_min=0.3, clip_symmetric=True, y=1.2)

    # view list
    @testmethod
    def view_attribute_list(self):
        returncode, output, error = self.run_program("--view-list")

    ## interface expressions
    @testmethod
    def read_cube(self):
        a = np.array([[1.0, -1.3], [1.3, -0.2]], dtype=cb.get_default_dtype())
        a.tofile("file_a.raw")
        returncode, output, error = self.run_program("""-e 'read_cube(filename="file_a.raw", shape=("{s}"), dtype="{t!r}")' '_r.sum()' --print""".format(
            s=Shape(a.shape),
            t=cb.get_dtype_name(a.dtype),
        ))
        self.assertEqual(returncode, 0)
        v = float(output.strip())
        self.assertAlmostEqual(v, a.sum())
    
    @testmethod
    def write_cube(self):
        returncode, output, error = self.run_program("""-e '_r = cb.as_dtype(np.array([[1.0, -1.3], [1.3, -0.2]]))' -e 'write_cube(filename="file_b.raw", cube=_r)'""")
        self.assertEqual(returncode, 0)
        self.assertFileExistsAndHasShape("file_b.raw", Shape("2x2"))
    
    @testmethod
    def write_cube_default(self):
        returncode, output, error = self.run_program("""-e '_r = cb.as_dtype(np.array([[1.0, -1.3], [1.3, -0.2]]))' -e 'write_cube(filename="file_c.raw")'""")
        self.assertEqual(returncode, 0)
        self.assertFileExistsAndHasShape("file_c.raw", Shape("2x2"))
