import os
import socket
import uuid

from docker_interface.core.plugins import Plugin
from docker_interface.core.util import get_free_port


class JupyterNotebookPlugin(Plugin):
    """
    Mount Google Cloud credentials in the Docker container.
    """
    ORDER = 960
    COMMANDS = ['run']

    def apply(self, configuration, schema, args):
        cmd = configuration.setdefault('run', {}).get('cmd', [])
        # Check whether the user is starting a notebook
        if cmd and cmd[:2] == ['jupyter', 'notebook']:
            # Don't try to start a browser
            cmd.append('--no-browser')
            # Open the standard port for the notebook
            free_port = get_free_port()
            configuration['run'].setdefault('publish', []).append({
                'container': 8888,
                'host': free_port,
            })

            if not any([x.startswith('--NotebookApp.token=') for x in cmd]):
                token = uuid.uuid4().hex
                cmd.append("--NotebookApp.token='%s'" % token)

            self.logger.info(
                "containerized notebook server will be available at http://%s:%d?token=%s",
                socket.gethostname(), free_port, token)

            if not any(x.startswith('--ip') for x in cmd):
                cmd.append('--ip=0.0.0.0')

        return configuration