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

import os


def build_parameter_parts(configuration, *parameters):
    """
    Construct command parts for one or more parameters.

    Parameters
    ----------
    configuration : dict
        configuration
    parameters : list
        list of parameters to create command line arguments for

    Yields
    ------
    argument : str
        command line argument
    """
    for parameter in parameters:
        values = configuration.pop(parameter, [])
        if values:
            if not isinstance(values, list):
                values = [values]
            for value in values:
                yield '--%s=%s' % (parameter, value)


def build_dict_parameter_parts(configuration, *parameters, **defaults):
    """
    Construct command parts for one or more parameters, each of which constitutes an assignment of
    the form `key=value`.

    Parameters
    ----------
    configuration : dict
        configuration
    parameters : list
        list of parameters to create command line arguments for
    defaults : dict
        default values to use if a parameter is missing

    Yields
    ------
    argument : str
        command line argument
    """
    for parameter in parameters:
        for key, value in configuration.pop(parameter, {}).items():
            yield '--%s=%s=%s' % (parameter, key, value)


def build_docker_run_command(configuration):
    """
    Translate a declarative docker `configuration` to a `docker run` command.

    Parameters
    ----------
    configuration : dict
        configuration

    Returns
    -------
    args : list
        sequence of command line arguments to run a command in a container
    """
    parts = configuration.pop('docker').split()
    parts.append('run')

    run = configuration.pop('run')

    # Ensure all env-files have proper paths
    if 'env-file' in run:
        run['env-file'] = [os.path.join(configuration['workspace'], env_file)
                           for env_file in run['env-file']]

    parts.extend(build_parameter_parts(
        run, 'user', 'workdir', 'rm', 'interactive', 'tty', 'env-file', 'cpu-shares', 'name',
        'network', 'label', 'memory', 'entrypoint', 'runtime', 'privileged'
    ))

    # Add the mounts
    # The following code requires docker >= 17.06
    '''for mount in run.pop('mount', []):
        if mount['type'] == 'bind':
            mount['source'] = os.path.join(
                configuration['workspace'], mount['source'])
        parts.extend(['--mount', ",".join(["%s=%s" % item for item in mount.items()])])'''

    # Add the mounts
    for mount in run.pop('mount', []):
        if mount['type'] == 'tmpfs':
            raise RuntimeError('tmpfs-mounts are currently not supported via the mount ' +
                               'directive in docker_interface. Consider using the tmpfs ' +
                               'directive instead.')
        if mount['type'] == 'bind':
           mount['source'] = os.path.abspath(
               os.path.join(configuration['workspace'], mount['source']))
        vol_config = '--volume=%s:%s' % (mount['source'], mount['destination'])
        if 'readonly' in mount and mount['readonly']:
            vol_config += ':ro'
        parts.append(vol_config)

    # Set or forward environment variables
    for key, value in run.pop('env', {}).items():
        if value is None:
            parts.append('--env=%s' % key)
        else:
            parts.append('--env=%s=%s' % (key, value))

    # Forward ports
    for publish in run.pop('publish', []):
        parts.append('--publish=%s:%s:%s' % tuple([
            publish.get(key, '') for key in "ip host container".split()]))

    # Add temporary file systems
    for tmpfs in run.pop('tmpfs', []):
        destination = tmpfs['destination']
        options = tmpfs.pop('options', [])
        for key in ['mode', 'size']:
            if key in tmpfs:
                options.append('%s=%s' % (key, tmpfs[key]))
        if options:
            destination = "%s:%s" % (destination, ",".join(options))
        parts.extend(['--tmpfs', destination])

    parts.append(run.pop('image'))
    parts.extend(run.pop('cmd', []))

    return parts


def build_docker_build_command(configuration):
    """
    Translate a declarative docker `configuration` to a `docker build` command.

    Parameters
    ----------
    configuration : dict
        configuration

    Returns
    -------
    args : list
        sequence of command line arguments to build an image
    """
    parts = configuration.pop('docker', 'docker').split()
    parts.append('build')

    build = configuration.pop('build')

    build['path'] = os.path.join(configuration['workspace'], build['path'])
    build['file'] = os.path.join(build['path'], build['file'])

    parts.extend(build_parameter_parts(
        build, 'tag', 'file', 'no-cache', 'quiet', 'cpu-shares', 'memory'))

    parts.extend(build_dict_parameter_parts(build, 'build-arg'))
    parts.append(build.pop('path'))

    return parts
