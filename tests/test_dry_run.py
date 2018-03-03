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

import glob
import json
from docker_interface import cli
import pytest


@pytest.fixture(params=glob.glob('tests/configurations/*.json'))
def configuration(request):
    with open(request.param) as fp:
        return json.load(fp)


@pytest.mark.parametrize('command', ['build', 'run'])
def test_cli(configuration, command):
    assert configuration is not None
    configuration['dry-run'] = True
    configuration['workspace'] = '.'
    # Run the command
    cli.entry_point([command], configuration)
