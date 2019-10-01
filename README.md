# Docker Interface [![Build Status](https://travis-ci.org/spotify/docker_interface.svg?branch=master)](https://travis-ci.org/spotify/docker_interface) ![Development Status](https://img.shields.io/badge/status-beta-orange.svg)

Docker Interface (DI) is a declarative interface for building images and running commands in containers using Docker. At Spotify, we use Docker Interface to minimise environment drift by running all of our code in containers–during development, production, or to train machine learning models.

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

Docker Interface can be invoked from the command line. By default, it reads the configuration from the file `di.yml` in the current working directory, a basic version of which is shown below.

```yaml
build:
  tag: name-of-your-image
```

Docker interface supports two commands:

* `build` builds and tags Docker image using the current working directory as the build context.
* `run` runs a Docker command in a container and mounts the current working directory with appropriate permissions at `/workspace` so you can access your local files without having to rebuild the image.

You can find more extensive examples in the [`examples` folder](https://github.com/spotify/docker_interface/tree/master/examples) in this repository. You can find more detailed information [here](http://docker-interface.readthedocs.io/en/latest/). Check the [schema](http://docker-interface.readthedocs.io/en/latest/schema.html) to get a comprehensive overview of the declarative syntax supported by Docker Interface.

## Contributing to Docker Interface

To contribute to the development of Docker Interface, please create a [fork](https://help.github.com/articles/fork-a-repo/) of the repository and send any changes as a pull request.

You can test your local installation of Docker Interface as follows.

```
# 0. Set up a virtual environment (optional but recommended)
# 1. Install development requirements
pip install -r requirements.txt
# 2. Run the tests
make tests
```

See [`virtualenv`](https://virtualenv.pypa.io/en/stable/) or [`conda`](https://conda.io/docs/) for details on how to set up a virtual environment in step 0.

## Code of conduct

This project adheres to the [Open Code of Conduct](https://github.com/spotify/code-of-conduct/blob/master/code-of-conduct.md). By participating, you are expected to honour this code.
