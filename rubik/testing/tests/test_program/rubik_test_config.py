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

from ....shape import Shape
from ....application import config
from ....application import environment
from ....cubes import api as cb

from ...rubik_test_program import RubikTestProgram
from ...rubik_test_case import testmethod

class RubikTestConfig(RubikTestProgram):
    METHOD_NAMES = []

    def setUp(self):
        super(RubikTestConfig, self).setUp()

    def impl_data_type(self, keys, actual_data_type=None, actual_file_format=None, const_value=None):
        shape = Shape("4x5")
        data_type = keys.get('data_type', 'float32')
        options = keys.get('options', None)
        dtype = cb.get_dtype(data_type)
        file_format = keys.get('file_format', 'raw')
        if actual_data_type is None:
            actual_data_type = data_type
        actual_dtype = cb.get_dtype(actual_data_type)
        if actual_file_format is None:
            actual_file_format = file_format
        rubik_dir = os.getcwd()
        rubik_config = config.get_config()
        rubik_config_data_type = os.path.join(rubik_dir, "rubik.config.{data_type}.{file_format}")
        rubik_config.default_data_type = data_type
        rubik_config.default_file_format = file_format
        if options is not None:
            rubik_config.default_options = options
        with open(rubik_config_data_type, "w") as f:
            rubik_config.write_config_file(f)
        current_rubik_dir = os.environ.get("RUBIK_DIR", None)
        current_rubik_config = os.environ.get("RUBIK_CONFIG", None)
        out_filename_format = 'ctmp_{shape}_{dtype}.{format}'
        out_filename = out_filename_format.format(shape=shape, dtype=actual_data_type, format=file_format)
        try:
            os.environ["RUBIK_DIR"] = rubik_dir
            os.environ["RUBIK_CONFIG"] = rubik_config_data_type
            environment.load_rubik_environment()
            returncode, output, error = self.run_program(
                """-e 'cb.const_cube("{s}", value={c})' -o '{o}'""".format(
                    s=shape,
                    c=const_value,
                    o=out_filename_format))
            self.assertEqual(returncode, 0)
            if actual_file_format == 'raw':
                self.assertFileExistsAndHasShape(out_filename, shape=shape, dtype=actual_data_type)
            else:
                self.assertFileExists(out_filename)
            returncode, output, error = self.run_program(
                """-i '{o}' -s {s} -e 'i0.sum()' --print""".format(
                    s=shape,
                    o=out_filename_format),
                join_stderr_stdout=False)
            value = actual_dtype(output.rstrip('\n'))
            self.assertEqual(value, shape.count() * const_value)
        finally:
            if current_rubik_dir is None:
                del os.environ["RUBIK_DIR"]
            else:
                os.environ["RUBIK_DIR"] = current_rubik_dir
            if current_rubik_config is None:
                del os.environ["RUBIK_CONFIG"]
            else:
                os.environ["RUBIK_CONFIG"] = rubik_config_data_type
            environment.load_rubik_environment()
            
    @testmethod
    def data_type_float64(self):
        return self.impl_data_type(keys=dict(data_type="float64"), const_value=0.35)

    @testmethod
    def data_type_float16(self):
        return self.impl_data_type(keys=dict(data_type="float16"), const_value=0.35)

    @testmethod
    def data_type_int64(self):
        return self.impl_data_type(keys=dict(data_type="int64"), const_value=3)

    @testmethod
    def data_type_int32(self):
        return self.impl_data_type(keys=dict(data_type="int32"), const_value=5)

    @testmethod
    def data_type_int16(self):
        return self.impl_data_type(keys=dict(data_type="int16"), const_value=8)

    @testmethod
    def data_type_int16_options_float64(self):
        return self.impl_data_type(keys=dict(data_type="int16", options=["--dtype", "float64"]), const_value=0.21, actual_data_type="float64")

    @testmethod
    def data_type_int32_file_format_text(self):
        return self.impl_data_type(keys=dict(data_type="int32", file_format='text'), const_value=5)

