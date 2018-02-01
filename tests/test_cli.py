import glob
import json
from docker_interface import cli
import pytest


@pytest.fixture
def configuration():
    with open('tests/data/comprehensive.json') as fp:
        return json.load(fp)

@pytest.fixture(params=[
    ['build'],
    ['run'],
    ['run', '--user', 'root']
])
def args(request):
    cmd, *args = request.param
    return [cmd, '--dry-run'] + args


def test_cli(args, configuration):
    assert configuration is not None
    cli.entry_point(args, configuration)


def test_cli_from_file():
    cli.entry_point(['-f', 'tests/data/comprehensive.json', 'build', '--dry-run'])
