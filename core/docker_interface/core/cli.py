import argparse
import json
import logging

import jsonschema

from .plugins import Plugin, BasePlugin
from . import json_util


def entry_point(args=None, configuration=None):
    """
    Standard entry point for the docker interface CLI.
    """
    # Parse basic information
    parser = argparse.ArgumentParser('di')
    base = BasePlugin()
    base.add_arguments(parser)
    args, remainder = parser.parse_known_args(args)
    command = args.command
    configuration = base.apply(configuration, None, args)

    logger = logging.getLogger('di')

    # Load all plugins and en/disable as desired
    plugin_cls = Plugin.load_plugins()
    plugins = configuration.get('plugins')
    if isinstance(plugins, list):
        plugins = [plugin_cls[name] for name in plugins]
    else:
        # Disable and enable specific plugins
        if isinstance(plugins, dict):
            try:
                for name in plugins.get('enable', []):
                    plugin_cls[name].ENABLED = True
                for name in plugins.get('disable', []):
                    plugin_cls[name].ENABLED = False
            except KeyError as ex:
                logger.fatal("could not resolve plugin %s. Available plugins: %s",
                             ex, ", ".join(plugin_cls))
                return 2
        elif plugins is not None:
            logger.fatal("'plugins' must be a `list`, `dict`, or `None` but got `%s`",
                         type(plugins))
            return 2

    # Restrict plugins to enabled ones
    plugins = list(sorted([cls() for cls in plugin_cls.values() if cls.ENABLED],
                          key=lambda x: x.ORDER))

    # Construct the schema
    schema = base.SCHEMA
    for cls in plugin_cls.values():
        schema = json_util.merge(schema, cls.SCHEMA)

    # Ensure that the plugins are relevant to the command
    plugins = [plugin for plugin in plugins
               if plugin.COMMANDS == 'all' or command in plugin.COMMANDS]
    parser = argparse.ArgumentParser('di %s' % command)
    for plugin in plugins:
        plugin.add_arguments(parser)
    args = parser.parse_args(remainder)

    # Apply defaults
    json_util.set_default_from_schema(configuration, schema)

    # Apply all the plugins in order
    logger.debug("configuration:\n%s", json.dumps(configuration, indent=4))
    for plugin in plugins:
        logger.debug("applying plugin '%s'", plugin)
        try:
            configuration = plugin.apply(configuration, schema, args)
            assert configuration is not None, "plugin '%s' returned `None`" % plugin
        except Exception as ex:  # pragma: no cover
            logger.fatal("failed to apply plugin '%s': %s", plugin, ex)
            raise
        logger.debug("configuration:\n%s", json.dumps(configuration, indent=4))
