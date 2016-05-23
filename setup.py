#  Copyright 2016 Gary Martin
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from setuptools import setup


requires = (
    'RPi.GPIO==0.6.2',
)
versions = (
    '0.1.0',
)

setup(
    name='pilights',
    version=versions[-1],
    description='Light show for Made In Sheffield exhibit',
    author='Gary Martin',
    author_email='gary.martin@physics.org',
    url='https://github.com/garym/pilights',
    install_requires=requires,
    py_modules=['pilights'],
    entry_points="""
        [console_scripts]
        pilights = pilights:main
    """,
)
