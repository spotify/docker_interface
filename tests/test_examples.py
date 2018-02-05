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
