# Docker Interface [![Build Status](https://travis-ci.com/spotify/docker_interface.svg?token=JxXwasVodA8iTGpTMh63&branch=master)](https://travis-ci.com/spotify/docker_interface)

Docker Interface (DI) is a declarative interface for building images and running commands in containers using Docker.

## Installing Docker Interface

You can install Docker Interface using the following `pip` command (you need a python3 interpreter).

```
pip install docker-interface
```


To check that Docker Interface was installed successfully, run
```
di --help
```

## Using Docker Interface

Docker Interface can be invoked from the command line. By default, it reads the configuration from the file `di.yml` in the current working directory and supports two commands:

* `build` builds a Docker image according to the configuration
* `run` runs a Docker command in a container

You can find specific examples in the `examples` folder in this repository. See readthedocs.org [link to be added once public] for more detailed documentation, and check the schema [link to be added once public] to get a comprehensive overview of the declarative syntax supported by Docker Interface.
