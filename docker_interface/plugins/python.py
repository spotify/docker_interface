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
import socket
import uuid

from .base import Plugin
from ..util import get_free_port


class JupyterPlugin(Plugin):
    """
    Forward the port required by Jupyter Notebook to the host machine and print a URL for easily
    accessing the notebook server.
    """
    ORDER = 960
    COMMANDS = ['run']

    def apply(self, configuration, schema, args):
        cmd = configuration.setdefault('run', {}).get('cmd', [])
        # Check whether the user is starting a notebook
        if cmd and cmd[0] == 'jupyter' and cmd[1] in ('notebook', 'lab'):
            # Don't try to start a browser
            cmd.append('--no-browser')
            # Open the standard port for the notebook
            free_port = get_free_port(range(8888, 9999))
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
