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
        'RubikError',
        'RubikMemoryError',
        'RubikUnitsError',
        'RubikDataTypeError',
        'RubikTestError',
]

import sys

class RubikError(Exception):
    pass

class RubikMemoryError(RubikError):
    pass

class RubikUnitsError(RubikError):
    pass

class RubikDataTypeError(RubikError):
    pass

class RubikTestError(RubikError):
    pass

class RubikExpressionError(RubikError):
    def __init__(self, message, expression_exception_info=None):
        super(RubikExpressionError, self).__init__(message)
        if expression_exception_info is None:
            expression_exception_info = sys.exc_info()
        self.expression_exception_info = expression_exception_info
