Plugins
=======

Docker Interface is a simple framework leveraging a suite of plugins to do most of its work. Each plugin is a :code:`python` class that defines at least two static attributes:

* :code:`COMANDS` is a sequence of commands such as :code:`run` or :code:`build` and defines for which command the plugin should be active. Setting :code:`COMMANDS` to :code:`all` will enable the plugin for all commands.
* :code:`ORDER` is an integer that determines the order of execution with lower numbers being executed earlier.

Furthermore, each plugin can additionally define:

* :code:`ENABLED` (defaults to :code:`True`) which indicates whether the plugin is enabled. Set :code:`ENABLED` to :code:`False` if you want a plugin to be disabled by default.
* :code:`SCHEMA` (defaults to :code:`{}`) is a JSON schema definition that is specific to the plugin. The Docker Interface configuration is validated against the union of schemas defined by all enabled plugins.

How plugins work
----------------

Each plugin has two methods used by Docker Interface:

* :code:`add_arguments(parser)` is called for each enabled plugin before Docker Interface attempts to parse the command line arguments. Each plugin may add arbitrary arguments to the :code:`parser` of the command line interface as long as they do not interfere with one another.
* :code:`apply(configuration, schema, args)` is called for each plugin after :code:`args` have been parsed. The :code:`schema` passed to the plugins is the union of all plugins' schemas. Finally, :code:`configuration` is the configuration returned by the :code:`apply` method of a plugin with lower :code:`ORDER`. The plugin may modify the configuration (as :code:`UserPlugin` does), execute a Docker command (as :code:`BuildExecutePlugin` does), or run any other python code.

Enable and disabling plugins
----------------------------

Unless otherwise specified, a plugin is enabled if and only if its class-level attribute :code:`ENABLED` is :code:`TRUE`. But you can specify which plugins to enable or disable in the configuration like so.

.. code-block:: yaml

    plugins:
      - user
      - homedir

The above configuration will enable only the :code:`user` and the :code:`homedir` plugins. Alternatively, you can specify which plugins to enable or disable explicitly.

.. code-block:: yaml

    plugins:
      enable:
        - user
      disable:
        - homedir

Which will enable the :code:`user` plugin, disable the :code:`homedir` plugin, and leave all other plugins unchanged.

Schema validation
-----------------

Docker Interface validates the configuration against the union of schemas defined by all enabled plugins. Different plugins may define the same schema as long as the definitions are consistent with one another. Schema definitions are also the preferred way to provide default values for the configuration. For example, the schema for the :code:`BasePlugin` responsible for loading the configuration, handling the workspace, and other global variables looks like so.

.. code-block:: json

    {
        "properties": {
            "workspace": {
                "type": "string",
                "description": "Path defining the DI workspace (absolute or relative to the URI of the configuration document). All subsequent path definitions must be absolute or relative to the `workspace`."
            },
            "docker": {
                "type": "string",
                "description": "Name of the docker CLI.",
                "default": "docker"
            }
        },
        "required": [
            "docker",
            "workspace"
        ]
    }

The configuration can define the parameters :code:`docker` and :code:`workspace`, and we provide a default value for :code:`docker`. We have omitted some properties for easier readability. If your plugin adds new configuration values, it should define a :code:`SCHEMA`.
