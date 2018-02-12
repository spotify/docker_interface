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

import pytest
import docker_interface as di
import docker_interface.cli


@pytest.fixture(params=[
    ('cython', ['python', '-c', '"add_two_numbers(1, 2)"']),
    ('ports', ['python bind_to_port.py']),
])
def example_definition(request):
    return request.param


@pytest.fixture
def build_image(example_definition):
    di.cli.entry_point(['-f', 'examples/%s/di.yml' % example_definition[0], 'build'])
    return example_definition


def test_command(build_image):
    example, command = build_image
    di.cli.entry_point(['-f', 'examples/%s/di.yml' % example, 'run'] + command)
