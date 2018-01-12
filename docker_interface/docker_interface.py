import os


def build_parameter_parts(configuration, *parameters):
    """
    Construct command parts for one or more parameters.
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
    the form `key = value`.
    """
    for parameter in parameters:
        for key, value in configuration.pop(parameter, {}).items():
            yield '--%s=%s=%s' % (parameter, key, value)


def build_docker_run_command(configuration):
    """
    Translate a declarative docker `configuration` to a `docker run` command.
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
        'network', 'label', 'memory', 'entrypoint'
    ))

    # Add the mounts
    # The following code requires docker >= 17.06
    '''for mount in run.pop('mount', []):
        if mount['type'] == 'bind':
            mount['source'] = os.path.join(configuration['workspace'], mount['source'])
        parts.extend(['--mount', ",".join(["%s=%s" % item for item in mount.items()])])'''

    # Add the mounts (support for legacy versions of docker)
    for mount in run.pop('mount', []):
       if mount['type'] == 'bind':
           # -v does not accept relative paths
           mount['source'] = os.path.abspath(os.path.join(configuration['workspace'], mount['source']))
       parts.append('--volume=%s:%s' % (mount['source'], mount['destination']))

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
        if options:
            destination = "%s:%s" % (destination, ",".join(options))
        parts.extend(['--tmpfs', destination])

    parts.append(run.pop('image'))
    parts.extend(run.pop('cmd', []))

    return parts


def build_docker_build_command(configuration):
    """
    Translate a declarative docker `configuration` to a `docker build` command.
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
