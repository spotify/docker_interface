import argparse
import functools as ft
import itertools as it
import logging
import os
import re

import jsonschema
import pkg_resources
import yaml

from .. import util


class Plugin:
    """
    Abstract base class for plugins.
    """
    ENABLED = True
    SCHEMA = {}
    ORDER = None
    COMMANDS = None

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.arguments = {}

    def add_argument(self, parser, path, name=None, schema=None, **kwargs):
        """
        Add an argument to the `parser` based on a schema definition.
        """
        schema = schema or self.SCHEMA
        name = name or ('--%s' % os.path.basename(path))
        self.arguments[name.strip('-')] = path
        # Build a path to the help in the schema
        path = util.split_path(path)
        path = os.path.sep.join(
            it.chain([os.path.sep], *zip(it.repeat("properties"), path)))
        property_ = util.get_value(schema, path)
        defaults = {
            'choices': property_.get('enum'),
            'help': property_.get('description')
        }
        if 'type' in property_:
            defaults['type'] = util.TYPES[property_['type']]
        defaults.update(kwargs)
        return parser.add_argument(name, **defaults)

    def add_arguments(self, parser):
        """
        Add arguments to the parser.
        """
        pass

    def apply(self, configuration, schema, args):
        """
        Apply the plugin to the configuration.
        """
        # Set values from the command line
        for name, path in self.arguments.items():
            value = getattr(args, name.replace('-', '_'))
            if value is not None:
                util.set_default(configuration, path, value)

        return configuration

    @staticmethod
    def load_plugins():
        """
        Load plugins.
        """
        plugin_cls = {}
        for entry_point in pkg_resources.iter_entry_points('docker_interface.plugins'):
            cls = entry_point.load()
            assert cls.COMMANDS is not None, \
                "plugin '%s' does not define its commands" % entry_point.name
            assert cls.ORDER is not None, \
                "plugin '%s' does not define its priority" % entry_point.name
            plugin_cls[entry_point.name] = cls
        return plugin_cls

    def cleanup(self):
        """
        Tear down the plugin and clean up any resources used.
        """
        pass

class ValidationPlugin(Plugin):
    """
    Validate the configuration document.
    """
    COMMANDS = 'all'
    ORDER = 990

    def apply(self, configuration, schema, args):
        super(ValidationPlugin, self).apply(configuration, schema, args)
        validator = jsonschema.validators.validator_for(schema)(schema)
        errors = list(validator.iter_errors(configuration))
        if errors: # pragma: no cover
            for error in errors:
                self.logger.fatal(error.message)
            raise ValueError("failed to validate configuration")
        return configuration


class ExecutePlugin(Plugin):
    """
    Base class for plugins that execute shell commands.

    Inheriting classes should define the method :code:`build_command` which takes a configuration
    document as its only argument.
    """
    def build_command(self, configuration):
        """
        Construct a command and return its parts.
        """
        raise NotImplementedError

    def add_arguments(self, parser):
        try:
            parser.add_argument('--dry-run', '-n', help="don't run any commands; just print them",
                                action='store_true')
        except argparse.ArgumentError as ex:
            if 'conflict' not in str(ex):
                raise

    def apply(self, configuration, schema, args):
        super(ExecutePlugin, self).apply(configuration, schema, args)
        parts = self.build_command(configuration)
        self.execute_command(parts, args.dry_run)
        return configuration

    def execute_command(self, parts, dry_run):
        """
        Execute a command.

        Parameters
        ----------
        parts : list
            Sequence of strings constituting a command.
        dry_run : bool
            Whether to just log the command instead of executing it.

        Returns
        -------
        status : int
            Status code of the executed command or `None` if `dry_run` is `True`.
        """
        if dry_run:
            self.logger.info("dry-run command '%s'", " ".join(map(str, parts)))
        else:  # pragma: no cover
            self.logger.debug("executing command '%s'", " ".join(map(str, parts)))
            return os.spawnvpe(os.P_WAIT, parts[0], parts, os.environ)


class BasePlugin(Plugin):
    """
    Load or create a default configuration and set up logging.
    """
    SCHEMA = {
        "title": "Declarative Docker Interface (DI) definition.",
        "$schema": "http://json-schema.org/draft-04/schema",
        "additionalProperties": False,
        "required": ["workspace", "docker"],
        "properties": {
            "workspace": {
                "type": "string",
                "description": "Path defining the DI workspace (absolute or relative to the URI of this document). All subsequent path definitions must be absolute or relative to the `workspace`."
            },
            "docker": {
                "type": "string",
                "description": "Name of the docker CLI.",
                "default": "docker"
            },
            "log-level": {
                "type": "string",
                "enum": ["debug", "info", "warning", "error", "critical", "fatal"],
                "default": "info"
            },
            "plugins": {
                "oneOf": [
                    {
                        "type": "array",
                        "description": "Enable the listed plugins and disable all plugins not listed.",
                        "items": {
                            "type": "string"
                        }
                    },
                    {
                        "type": "object",
                        "properties": {
                            "enable": {
                                "type": "array",
                                "description": "Enable the listed plugins.",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "disable": {
                                "type": "array",
                                "description": "Disable the listed plugins.",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "additionalProperties": False
                    }
                ]
            }
        }
    }

    def add_arguments(self, parser):
        parser.add_argument('--file', '-f', help='Configuration file.', default='di.yml')
        self.add_argument(parser, '/workspace')
        self.add_argument(parser, '/docker')
        self.add_argument(parser, '/log-level')
        parser.add_argument('command', help='Docker interface command to execute.',
                            choices=['run', 'build'])

    def apply(self, configuration, schema, args):
        # Load the configuration
        if os.path.isfile(args.file):
            filename = os.path.abspath(args.file)
            with open(filename) as fp:  # pylint: disable=invalid-name
                configuration = yaml.load(fp)
            self.logger.debug("loaded configuration from '%s'", filename)
            dirname = os.path.dirname(filename)
            configuration['workspace'] = os.path.join(dirname, configuration.get('workspace', '.'))
        elif args.file == 'di.yml':
            self.logger.warning(
                "using empty configuration because no 'di.yml' file could be found")
            configuration = configuration or {}
            configuration.setdefault('workspace', os.getcwd())
        else:
            raise FileNotFoundError(
                "could not find configuration file '%s'" % args.file)

        configuration = super(BasePlugin, self).apply(configuration, schema, args)

        logging.basicConfig(level=configuration.get('log-level', 'info').upper())
        return configuration


class SubstitutionPlugin(Plugin):
    """
    Substitute variables in strings.

    String values in the configuration document may

    * reference other parts of the configuration document using :code:`#{path}`, where :code:`path`
      may be an absolute or relative path in the document.
    * reference a variable using :code:`${path}`, where :code:`path` is assumed to be an absolute
      path in the :code:`VARIABLES` class attribute of the plugin.

    By default, the plugin provides environment variables using the :code:`env` prefix. For example,
    a value could reference the user name on the host using :code:`${env/USER}`. Other plugins can
    provide variables for substitution by extending the :code:`VARIABLES` class attribute and should
    do so using a unique prefix.
    """
    REF_PATTERN = re.compile(r'#\{(?P<path>.*?)\}')
    VAR_PATTERN = re.compile(r'\$\{(?P<path>.*?)\}')
    COMMANDS = 'all'
    ORDER = 980
    VARIABLES = {
        'env': dict(os.environ)
    }

    @classmethod
    def substitute_variables(cls, configuration, value, ref):
        """
        Substitute varibles in `value` from `configuration` where any path reference is relative to
        `ref`.
        """
        if isinstance(value, str):
            while True:
                match = cls.REF_PATTERN.search(value)
                if match is None:
                    break
                path = os.path.join(os.path.dirname(ref), match.group('path'))
                try:
                    value = value.replace(
                        match.group(0), str(util.get_value(configuration, path)))
                except KeyError:
                    raise KeyError(path)

            while True:
                match = cls.VAR_PATTERN.search(value)
                if match is None:
                    break
                value = value.replace(
                    match.group(0),
                    str(util.get_value(cls.VARIABLES, match.group('path'), '/')))
        return value

    def apply(self, configuration, schema, args):
        super(SubstitutionPlugin, self).apply(configuration, schema, args)
        return util.apply(configuration, ft.partial(self.substitute_variables, configuration))


class WorkspaceMountPlugin(Plugin):
    """
    Mount the workspace inside the container.
    """
    SCHEMA = {
        "properties": {
            "run": {
                "properties": {
                    "workspace-dir": {
                        "type": "string",
                        "description": 'Path at which to mount the workspace in the container.',
                        "default": "/workspace"
                    },
                    "workdir": {
                        "type": "string",
                        "default": "#{workspace-dir}"
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }
    COMMANDS = ['run']
    ORDER = 500

    def add_arguments(self, parser):
        self.add_argument(parser, '/run/workspace-dir')

    def apply(self, configuration, schema, args):
        super(WorkspaceMountPlugin, self).apply(configuration, schema, args)
        configuration['run'].setdefault('mount', []).append({
            'type': 'bind',
            'source': '#{/workspace}',
            'destination': util.get_value(configuration, '/run/workspace-dir')
        })
        return configuration


class HomeDirPlugin(Plugin):
    """
    Mount an ephemeral home directory in the container.
    """
    ORDER = 520
    COMMANDS = ['run']

    def apply(self, configuration, schema, args):
        super(HomeDirPlugin, self).apply(configuration, schema, args)
        configuration['run'].setdefault('tmpfs', []).append({
            'destination': '#{/run/env/HOME}',
            'options': ['exec']
        })
        configuration['run'].setdefault('env', {}).setdefault('HOME', '/${user/name}')
        return configuration
