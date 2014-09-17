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
           'RubikTestInputOutput',
          ]

import numpy as np

from rubik.cubes import api as cb
from rubik.shape import Shape

from ...rubik_test_case import RubikTestCase, testmethod

class RubikTestDtypes(RubikTestCase):
    METHOD_NAMES = []

    @testmethod
    def test_get_dtype(self):
        self.assertEqual(cb.get_dtype("float32"), cb.get_dtype(np.float32))
        self.assertEqual(cb.get_dtype("float32"), cb.get_dtype(None))
        self.assertEqual(cb.get_dtype("int64"), cb.get_dtype(np.int64))
        a = np.array([1.5, 2.4], dtype=np.float64)
        self.assertEqual(cb.get_dtype(a.dtype), cb.get_dtype(np.float64))

    @testmethod
    def test_get_default_dtype(self):
        self.assertEqual(cb.get_dtype_name(cb.get_default_dtype()), "float32")

    @testmethod
    def test_get_dtype_name_float(self):
        self.assertEqual(cb.get_dtype_name("float32"), "float32")
        self.assertEqual(cb.get_dtype_name(np.float32), "float32")

    @testmethod
    def test_get_dtype_name_int(self):
        a = np.array([1.5, 2.4], dtype=np.float64)
        self.assertEqual(cb.get_dtype_name(cb.as_dtype(a, dtype="int32").dtype), "int32")
        self.assertEqual(cb.get_dtype_name(cb.as_dtype(a).dtype), cb.get_dtype_name(cb.get_dtype(None)))

    @testmethod
    def test_best_precise_dtype_int(self):
        for npt in np.int8, np.int16, np.int32, np.int64:
            self.assertEqual(cb.best_precise_dtype(npt), np.int64)

    @testmethod
    def test_best_precise_dtype_uint(self):
        for npt in np.uint8, np.uint16, np.uint32, np.uint64:
            self.assertEqual(cb.best_precise_dtype(npt), np.uint64)

    @testmethod
    def test_best_precise_dtype_float(self):
        for npt in np.float_, np.float16, np.float32, np.float64:
            self.assertEqual(cb.best_precise_dtype(npt), np.float64)

    @testmethod
    def test_best_precise_dtype_complex(self):
        for npt in np.complex_, np.complex64, np.complex128:
            self.assertEqual(cb.best_precise_dtype(npt), np.complex128)

