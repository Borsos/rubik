#
# Copyright 2013 Simone Campagna
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

from distutils.core import setup
import os
import sys

scripts = [
	'bin/rubik_test',
]

try:
    dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
    py_dirname = os.path.join(dirname, "..")
    sys.path.insert(0, py_dirname)

    from rubik import conf
finally:
    del sys.path[0]

setup(
    name = "python-rubik-testing",
    version = conf.VERSION,
    requires = [],
    description = "Testing library/application for rubik",
    author = "Simone Campagna",
    author_email = "simone.campagna@tiscali.it",
    url="https://github.com/simone-campagna/rubik",
    packages = ["rubik_testing",
                "rubik_testing.application",
                "rubik_testing.tests",
                "rubik_testing.tests.test_base",
                "rubik_testing.tests.test_cubes",
                "rubik_testing.tests.test_help",
                "rubik_testing.tests.test_program",
               ],
    scripts = scripts,
    package_data = {},
)

