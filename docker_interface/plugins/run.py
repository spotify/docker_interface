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

import argparse
import sys
from ..docker_interface import build_docker_run_command
from .. import util
from .base import Plugin, ExecutePlugin


class RunPlugin(ExecutePlugin):
    """
    Run a command inside a docker container.
    """
    COMMANDS = ['run']
    ORDER = 1000
    build_command = staticmethod(build_docker_run_command)


class RunConfigurationPlugin(Plugin):
    """
    Configure how to run a command inside a docker container.
    """
    COMMANDS = ['run']
    ORDER = 950
    SCHEMA = {
        "properties": {
            "run": {
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Image to derive the container from.",
                        "default": "#{/build/tag}"
                    },
                    "env": {
                        "type": "object",
                        "description": "Set environment variables (use `null` to forward environment variables).",
                        "additionalProperties": {
                            "type": [
                                "string",
                                "null"
                            ]
                        }
                    },
                    "env-file": {
                        "type": "array",
                        "description": "Read in a file of environment variables.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "mount": {
                        "type": "array",
                        "description": "Attach a filesystem mount to the container.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "bind",
                                        "tmpfs",
                                        "volume"
                                    ]
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Volume name or path on the host."
                                },
                                "destination": {
                                    "type": "string",
                                    "description": "Absolute mount path in the container."
                                },
                                "readonly": {
                                    "type": "boolean",
                                    "description": "Whether to mount the volume read-only."
                                }
                            },
                            "required": [
                                "type",
                                "destination"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "publish": {
                        "type": "array",
                        "description": "Publish a container's port(s), or range(s) of ports, to the host.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ip": {
                                    "type": "string",
                                    "description": ""
                                },
                                "host": {
                                    "anyOf": [
                                        {
                                            "type": "number"
                                        },
                                        {
                                            "type": "string",
                                            "pattern": "\\d+-\\d+"
                                        }
                                    ],
                                    "description": "Port (e.g. `8000`) or range of ports (e.g. `8000-8100`) on the host."
                                },
                                "container": {
                                    "anyOf": [
                                        {
                                            "type": "number"
                                        },
                                        {
                                            "type": "string",
                                            "pattern": "\\d+-\\d+"
                                        }
                                    ],
                                    "description": "Port (e.g. `8000`) or range of ports (e.g. `8000-8100`) on the container."
                                }
                            },
                            "required": [
                                "container"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "runtime": {
                        "type": "string",
                        "description": "Runtime to use for this container."
                    },
                    "tmpfs": {
                        "type": "array",
                        "description": "Mount a tmpfs directory",
                        "items": {
                            "type": "object",
                            "properties": {
                                "destination": {
                                    "type": "string",
                                    "description": "Absolute mount path in the container."
                                },
                                "options": {
                                    "type": "array",
                                    "description": "Mount options for the temporary file system.",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "size": {
                                    "type": "integer",
                                    "description": "Size of the tmpfs mount in bytes."
                                },
                                "mode": {
                                    "type": "integer",
                                    "description": "File mode of the tmpfs in octal."
                                }
                            },
                            "required": [
                                "destination"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "cmd": {
                        "type": "array",
                        "description": "Command to execute inside the container.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "tty": {
                        "type": "boolean",
                        "description": "Allocate a pseudo-TTY"
                    },
                    "cpu-shares": {
                        "type": "integer",
                        "description": "CPU shares (relative weight)",
                        "minimum": 0,
                        "maximum": 1024
                    },
                    "name": {
                        "type": "string",
                        "description": "Assign a name to the container"
                    },
                    "network": {
                        "type": "string",
                        "description": "Connect a container to a network (default \"default\")"
                    },
                    "label": {
                        "type": "array",
                        "description": "Set meta data on a container"
                    },
                    "rm": {
                        "type": "boolean",
                        "description": "Automatically remove the container when it exits",
                        "default": True
                    },
                    "privileged": {
                        "type": "boolean",
                        "description": "Give extended privileges to this container",
                        "default": False
                    },
                    "memory": {
                        "type": "string",
                        "description": "Memory limit"
                    },
                    "interactive": {
                        "type": "boolean",
                        "description": "Keep STDIN open even if not attached"
                    },
                    "entrypoint": {
                        "type": "string",
                        "description": "Overwrite the default ENTRYPOINT of the image"
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Working directory inside the container"
                    },
                    "user": {
                        "type": "string",
                        "description": "Username or UID (format: <name|uid>[:<group|gid>])"
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    def add_arguments(self, parser):
        super(RunConfigurationPlugin, self).add_arguments(parser)
        self.add_argument(parser, '/run/cmd', name='cmd', nargs=argparse.REMAINDER, type=None)

    def apply(self, configuration, schema, args):
        super(RunConfigurationPlugin, self).apply(configuration, schema, args)
        # Set some sensible defaults (could also be published as variables)
        util.set_default(configuration, '/run/tty', sys.stdout.isatty())
        util.set_default(configuration, '/run/interactive', sys.stdout.isatty())
        return configuration
