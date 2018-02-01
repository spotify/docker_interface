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
    assert cli.entry_point([command], configuration) == 0
