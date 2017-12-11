from setuptools import setup

PLUGINS = ['GoogleCloudCredentials', 'GoogleDockerAuthorization']

setup(
    name="docker_interface_google",
    version="0.1",
    packages=['docker_interface.google'],
    install_requires=[
        'jsonschema==2.6.0'
    ],
    entry_points={
        'docker_interface.plugins': [
            '%s = docker_interface.google.plugins:%sPlugin' % (name.lower(), name)
            for name in PLUGINS
        ],
    }
)
