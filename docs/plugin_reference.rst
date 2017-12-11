Plugin reference
================

This document lists all plugins in order of execution.

BasePlugin
----------


Load or create a default configuration and set up logging.


Properties
~~~~~~~~~~

* workspace (:code:`string`): Path defining the DI workspace (absolute or relative to the URI of this document). All subsequent path definitions must be absolute or relative to the `workspace`.
* docker (:code:`string`): Name of the docker CLI.
* log-level (:code:`string`): 
* plugins: 

GoogleDockerAuthorizationPlugin
-------------------------------


Configure docker authorization for Google services such as Google Container Registry.



WorkspaceMountPlugin
--------------------


Mount the workspace inside the container.


Properties
~~~~~~~~~~

* run: 
    * workspace-dir (:code:`string`): Path at which to mount the workspace in the container.
    * workdir: 

UserPlugin
----------


Share the host user id and group id with the container.

The plugin provides the following additional variables for substitution:

* :code:`user/name`: Name of the user on the host.
* :code:`user/uid`: User id of the user on the host.
* :code:`group/name`: Name of the user group on the host.
* :code:`group/gid`: Group id of the user group on the host.


Properties
~~~~~~~~~~

* run: 
    * user (:code:`string`): Username or UID (format: <name|uid>[:<group|gid>])

HomeDirPlugin
-------------


Mount an ephemeral home directory in the container.



GoogleCloudCredentialsPlugin
----------------------------


Mount Google Cloud credentials in the Docker container.



BuildConfigurationPlugin
------------------------


Configure how to build a docker image.


Properties
~~~~~~~~~~

* build: 
    * path (:code:`string`): Path of the build context.
    * tag (:code:`string`): Name and optionally a tag in the 'name:tag' format.
    * file (:code:`string`): Name of the Dockerfile.
    * build-arg (:code:`object`): Set build-time variables.
    * no-cache (:code:`boolean`): Do not use cache when building the image
    * quiet (:code:`boolean`): Suppress the build output and print image ID on success
    * cpu-shares (:code:`integer`): CPU shares (relative weight)
    * memory (:code:`string`): Memory limit

RunConfigurationPlugin
----------------------


Configure how to run a command inside a docker container.


Properties
~~~~~~~~~~

* run: 
    * cmd (:code:`array`): Command to execute inside the container.
    * image (:code:`string`): Image to derive the container from.
    * env (:code:`object`): Set environment variables (use `null` to forward environment variables).
    * env_file (:code:`array`): Read in a file of environment variables.
    * mount (:code:`array`): Attach a filesystem mount to the container.
    * publish (:code:`array`): Publish a container's port(s) to the host.
    * tmpfs (:code:`array`): Mount a tmpfs directory
    * tty (:code:`boolean`): Allocate a pseudo-TTY
    * cpu-shares (:code:`integer`): CPU shares (relative weight)
    * name (:code:`string`): Assign a name to the container
    * network (:code:`string`): Connect a container to a network (default "default")
    * label (:code:`array`): Set meta data on a container
    * rm (:code:`boolean`): Automatically remove the container when it exits
    * memory (:code:`string`): Memory limit
    * interactive (:code:`boolean`): Keep STDIN open even if not attached
    * entrypoint (:code:`string`): Overwrite the default ENTRYPOINT of the image
    * workdir (:code:`string`): Working directory inside the container
    * user (:code:`string`): Username or UID (format: <name|uid>[:<group|gid>])

SubstitutionPlugin
------------------


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



ValidationPlugin
----------------


Validate the configuration document.



BuildPlugin
-----------


Build a docker image.



RunPlugin
---------


Run a command inside a docker container.


