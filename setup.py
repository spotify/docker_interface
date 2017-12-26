from setuptools import setup, find_packages

PLUGINS = [
    'Run', 'Build', 'WorkspaceMount', 'Substitution', 'User', 'HomeDir', 'RunConfiguration',
    'BuildConfiguration', 'Validation', 'GoogleCloudCredentials', 'GoogleContainerRegistry',
    'Jupyter'
]

setup(
    name="docker_interface",
    version="0.2.4",
    packages=find_packages(),
    install_requires=[
        'jsonschema==2.6.0',
        'pyaml==17.10.0',
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
    url="https://ghe.spotify.net/sonalytic/docker_interface/",
)
