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
	'bin/rubik',
]

dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
py_dirname = os.path.join(dirname, "lib", "python")
sys.path.insert(0, py_dirname)

from rubik import conf

setup(
    name = "rubik",
    version = conf.VERSION,
    requires = [],
    description = "Tool to read/write N-dimensional cubes",
    author = "Simone Campagna",
    author_email = "simone.campagna@tiscali.it",
    url="https://github.com/simone-campagna/rubik",
    download_url = 'https://github.com/simone-campagna/rubik/tarball/{}.tar.gz'.format(conf.VERSION),
    packages = ["rubik",
                "rubik.application",
                "rubik.application.help_functions",
                "rubik.cubes",
                "rubik.visualizer",
                "rubik.visualizer.impl"
               ],
    scripts = scripts,
    package_data = {},
)

