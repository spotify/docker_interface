from setuptools import setup

PLUGINS = [
    'Run', 'Build', 'WorkspaceMount', 'Substitution', 'User', 'HomeDir', 'RunConfiguration',
    'BuildConfiguration', 'Validation'
]

setup(
    name="docker_interface_core",
    version="0.1",
    packages=['docker_interface.core'],
    install_requires=[
        'jsonschema==2.6.0',
        'PyYAML==3.12',
    ],
    entry_points={
        'console_scripts': [
            'di = docker_interface.core.cli:entry_point'
        ],
        'docker_interface.plugins': [
            '%s = docker_interface.core.plugins:%sPlugin' % (name.lower(), name) for name in PLUGINS
        ],
    }
)
