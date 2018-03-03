# Copyright 2018 Spotify AB

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import logging

from .plugins import Plugin, BasePlugin
from . import util


def entry_point(args=None, configuration=None):
    """
    Standard entry point for the docker interface CLI.

    Parameters
    ----------
    args : list or None
        list of command line arguments or `None` to use `sys.argv`
    configuration : dict
        parsed configuration or `None` to load and build a configuration given the command line
        arguments

    Raises
    ------
    SystemExit
        if the configuration is malformed or the docker subprocesses returns a non-zero status code
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
        plugins = [plugin_cls[name.lower()] for name in plugins]
    else:
        # Disable and enable specific plugins
        if isinstance(plugins, dict):
            try:
                for name in plugins.get('enable', []):
                    plugin_cls[name.lower()].ENABLED = True
                for name in plugins.get('disable', []):
                    plugin_cls[name.lower()].ENABLED = False
            except KeyError as ex:  # pragma: no cover
                logger.fatal("could not resolve plugin %s. Available plugins: %s",
                             ex, ", ".join(plugin_cls))
                raise SystemExit(2)
        elif plugins is not None:  # pragma: no cover
            logger.fatal("'plugins' must be a `list`, `dict`, or `None` but got `%s`",
                         type(plugins))
            raise SystemExit(2)

    # Restrict plugins to enabled ones
    plugins = list(sorted([cls() for cls in plugin_cls.values() if cls.ENABLED],
                          key=lambda x: x.ORDER))

    # Construct the schema
    schema = base.SCHEMA
    for cls in plugin_cls.values():
        schema = util.merge(schema, cls.SCHEMA)

    # Ensure that the plugins are relevant to the command
    plugins = [plugin for plugin in plugins
               if plugin.COMMANDS == 'all' or command in plugin.COMMANDS]
    parser = argparse.ArgumentParser('di %s' % command)
    for plugin in plugins:
        plugin.add_arguments(parser)
    args = parser.parse_args(remainder)

    # Apply defaults
    util.set_default_from_schema(configuration, schema)

    # Apply all the plugins in order
    status_code = 0
    logger.debug("configuration:\n%s", json.dumps(configuration, indent=4))
    for plugin in plugins:
        logger.debug("applying plugin '%s'", plugin)
        try:
            configuration = plugin.apply(configuration, schema, args)
            assert configuration is not None, "plugin '%s' returned `None`" % plugin
        except Exception as ex:  # pragma: no cover
            logger.exception("failed to apply plugin '%s': %s", plugin, ex)
            message = "please rerun the command using `di --log-level debug` and file a new " \
                      "issue containing the output of the command here: https://github.com/" \
                      "spotify/docker_interface/issues/new"
            logger.fatal("\033[%dm%s\033[0m", 31, message)
            status_code = 3
            break
        logger.debug("configuration:\n%s", json.dumps(configuration, indent=4))

    for plugin in reversed(plugins):
        logger.debug("tearing down plugin '%s'", plugin)
        plugin.cleanup()

    status_code = configuration.get('status-code', status_code)
    if status_code:
        raise SystemExit(status_code)
