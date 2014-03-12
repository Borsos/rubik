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

from distutils.core import setup
import os

scripts = [
	'cubist',
]


setup(
    name = "cubist",
    version = "1.0.0",
    requires = [],
    description = "Tool to read/write N-dimensional cubes",
    author = "Simone Campagna",
    author_email = "simone.campagna@tiscali.it",
    url="https://github.com/simone-campagna/cubist",
    packages = ["cubist", "cubist.application"],
    package_dir = {"cubist": "lib/python/cubist"},
    scripts = scripts,
    package_data = {},
)

