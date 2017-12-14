from setuptools import setup, find_packages

PLUGINS = [
    'Run', 'Build', 'WorkspaceMount', 'Substitution', 'User', 'HomeDir', 'RunConfiguration',
    'BuildConfiguration', 'Validation'
]

setup(
    name="docker_interface_core",
    version="0.2.3",
    packages=['docker_interface.%s' % pkg for pkg in find_packages('docker_interface')],
    install_requires=[
        'jsonschema==2.6.0',
        'pyaml==17.10.0',
    ],
    entry_points={
        'console_scripts': [
            'di = docker_interface.core.cli:entry_point'
        ],
        'docker_interface.plugins': [
            '%s = docker_interface.core.plugins:%sPlugin' % (name.lower(), name) for name in PLUGINS
        ],
    },
    author="Till Hoffmann",
    author_email="till@spotify.com",
    url="https://ghe.spotify.net/till/docker_interface/",
)
