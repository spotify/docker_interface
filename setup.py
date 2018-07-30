# Copyright 2018 Spotify AB

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

PLUGINS = [
    'Run', 'Build', 'WorkspaceMount', 'Substitution', 'User', 'HomeDir', 'RunConfiguration',
    'BuildConfiguration', 'Validation', 'GoogleCloudCredentials', 'GoogleContainerRegistry',
    'Jupyter'
]


with open('README.md') as fp:
    long_description = fp.read()


setup(
    name="docker_interface",
    version="0.2.12",
    packages=find_packages(),
    install_requires=[
        'jsonschema>=2.6.0',
        'PyYAML>=3.12',
    ],
    entry_points={
        'console_scripts': [
            'di = docker_interface.cli:entry_point'
        ],
        'docker_interface.plugins': [
            '%s = docker_interface.plugins:%sPlugin' % (name.lower(), name) for name in PLUGINS
        ],
    },
    author="Till Hoffmann",
    author_email="till@spotify.com",
    url="https://github.com/spotify/docker_interface",
    license="License :: OSI Approved :: Apache Software License",
    description="Declarative interface for building images and running commands in containers "
                "using Docker.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
