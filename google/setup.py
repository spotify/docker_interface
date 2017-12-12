from setuptools import setup, find_packages

PLUGINS = ['GoogleCloudCredentials', 'GoogleDockerAuthorization']

setup(
    name="docker_interface_google",
    version="0.2.3",
    packages=['docker_interface.%s' % pkg for pkg in find_packages('docker_interface')],
    install_requires=[
        'jsonschema==2.6.0'
    ],
    entry_points={
        'docker_interface.plugins': [
            '%s = docker_interface.google.plugins:%sPlugin' % (name.lower(), name)
            for name in PLUGINS
        ],
    },
    author="Till Hoffmann",
    author_email="till@spotify.com",
    url="https://ghe.spotify.net/till/docker_interface/",
)
