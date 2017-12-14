Introduction
============

`Docker <www.docker.com>`_ provides a containerised runtime that enables easy and reproducible deployment of applications to production. Unfortunately, these applications are often developed using the local environment of the developer such that it can be difficult to reproduce the results on another machine. Using Docker as a development environment is possible in principle but plagued by problems in practice. For example,

* `mounting a folder from the host in the container can cause permission problems <https://stackoverflow.com/questions/23544282/what-is-the-best-way-to-manage-permissions-for-docker-shared-volumes>`_,
* `ports need to be manually forwarded to run Jupyter notebook servers <https://hub.docker.com/r/jupyter/base-notebook/>`_,
* or `credentials are not available inside the container <https://stackoverflow.com/questions/42307210/user-google-cloud-credentials-inside-ephemeral-container>`_.

These issues can be addressed directly by modifying the arguments passed to the Docker `command line interface <https://docs.docker.com/engine/reference/commandline/cli/>`_ (CLI), but the resulting commands can be formidable. Docker Interface allows users to define a Docker command declaratively in a configuration file rather than having to remember to type out all required arguments on the command line. In short, Docker Interface is a translator from a command declaration to a Docker command.

Installing Docker interface
---------------------------

You can install Docker Interface from Artifactory using the following command (you need a python3 interpreter).

.. code-block:: bash

   pip install docker-interface -i https://artifactory.spotify.net/artifactory/api/pypi/pypi/simple/


To check that Docker Interface was installed successfully, run

.. code-block:: bash

   di --help


Using Docker Interface
----------------------

Docker Interface will attempt to locate a configuration file :code:`di.yml` in the current working directory. A basic configuration (as a YAML or JSON file) might look like so.

.. code-block:: yaml

   docker: docker  # The docker command to use, e.g. nvidia-docker
   workspace: .    # The workspace path (relative to the directory containing the configuration)

All paths in the configuration are relative to the :code:`workspace`. The values shown above are default values and you can omit them unless you want to change them.

Docker Interface supports two commands:

* `build <https://docs.docker.com/engine/reference/commandline/build/>`_ to build a Docker image,
* and `run <https://docs.docker.com/engine/reference/commandline/run/>`_ to execute a command inside a Docker container.

Information that is relevant to a particular command is stored in a corresponding section of the configuration file. For example, you can run the :code:`bash` shell in the latest :code:`ubuntu` like so: First, create the following configuration file.

.. code-block:: yaml

   run:
     image: ubuntu

Second, run :code:`di run bash` from the command line. In contrast to :code:`docker run ubuntu bash`, the :code:`di` command will open an interactive shell because it starts the container interactively if it detects that Docker Interface was launched interactively. By default, it will also create an ephemeral container which is deleted as soon as you log out of the shell.

Before delving into the plugin architecture that powers Docker Interface, let us consider a simple example for building your own Docker image. Create a :code:`Dockerfile` with the following content

.. code-block:: Dockerfile

   FROM python
   RUN pip install ipython

and modify your :code:`di.yml` configuration to read:

.. code-block:: yaml

   build:
     tag: my-ipython

Running :code:`di build` from the command line will build your image, and :code:`di run ipython` will run the :code:`ipython` command inside the container. Unless otherwise specified, Docker Interface uses the image built in the :code:`build` step to start a new container when you use the :code:`run` command.

A comprehensive list of variables that can be set in the :code:`di.yml` configuration can be found in the :doc:`plugin_reference`.
