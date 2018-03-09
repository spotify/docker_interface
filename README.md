# Docker Interface [![Build Status](https://travis-ci.com/spotify/docker_interface.svg?token=JxXwasVodA8iTGpTMh63&branch=master)](https://travis-ci.com/spotify/docker_interface) ![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)

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

You can find specific examples in the `examples` folder in this repository. See http://docker-interface.readthedocs.io/en/latest/ for more detailed documentation, and check the [schema](http://docker-interface.readthedocs.io/en/latest/schema.html) to get a comprehensive overview of the declarative syntax supported by Docker Interface.

## Contributing to Docker Interface

To contribute to the development of Docker Interface, please create a [fork](https://help.github.com/articles/fork-a-repo/) of the repository and send any changes as a pull request.

You can test your local installation of Docker Interface as follows.

```
# 0. Set up a virtual environment (optional but recommended)
# 1. Install development requirements
pip install -r requirements.txt
# 2. Install docker interface in editable mode
pip install -e .
# Run the tests
make tests
```

See [`virtualenv`](https://virtualenv.pypa.io/en/stable/) or [`conda`](https://conda.io/docs/) for details on how to set up a virtual environment in step 0.

## Code of conduct

This project adheres to the [Open Code of Conduct][code-of-conduct]. By participating, you are expected to honour this code.

[code-of-conduct]: https://github.com/spotify/code-of-conduct/blob/master/code-of-conduct.md
