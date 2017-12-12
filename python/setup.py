from setuptools import setup

PLUGINS = ['JupyterNotebook']

setup(
    name="docker_interface_python",
    version="0.2",
    packages=['docker_interface.python'],
    install_requires=[
        'jsonschema==2.6.0'
    ],
    entry_points={
        'docker_interface.plugins': [
            '%s = docker_interface.python.plugins:%sPlugin' % (name.lower(), name)
            for name in PLUGINS
        ],
    },
    author="Till Hoffmann",
    author_email="till@spotify.com",
    url="https://ghe.spotify.net/till/docker_interface/",
)
