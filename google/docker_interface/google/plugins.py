import os
from docker_interface.core.plugins import Plugin


class GoogleCloudCredentialsPlugin(Plugin):
    """
    Mount Google Cloud credentials in the Docker container.
    """
    ORDER = 560
    COMMANDS = ['run']

    def apply(self, configuration, schema, args):
        configuration['build'].setdefault('mount', []).append({
            'type': 'bind',
            'source': '${env/HOME}/.config/gcloud',
            'destination': '#{/run/env/HOME}/.config/gcloud'
        })
        return configuration


class GoogleDockerAuthorizationPlugin(Plugin):
    """
    Configure docker authorization for Google services such as Google Container Registry.
    """
    # We want to authorize before any other plugins that may depend on access to Google's services.
    ORDER = 10
    COMMANDS = ['run']

    def apply(self, configuration, schema, args):
        parts = ['gcloud', 'docker', '--authorize-only']
        os.spawnvpe(os.P_WAIT, parts[0], parts, os.environ)
        return configuration
