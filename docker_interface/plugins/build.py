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

from .base import Plugin, ExecutePlugin
from ..docker_interface import build_docker_build_command


class BuildPlugin(ExecutePlugin):
    """
    Build a docker image.
    """
    COMMANDS = ['build']
    ORDER = 1000
    build_command = staticmethod(build_docker_build_command)


class BuildConfigurationPlugin(Plugin):
    """
    Configure how to build a docker image.
    """
    COMMANDS = ['build']
    ORDER = 950
    SCHEMA = {
        "properties": {
            "build": {
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the build context.",
                        "default": "#{/workspace}"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Name and optionally a tag in the 'name:tag' format.",
                        "default": "docker-interface-image"
                    },
                    "file": {
                        "type": "string",
                        "description": "Name of the Dockerfile.",
                        "default": "#{path}/Dockerfile"
                    },
                    "build-arg": {
                        "type": "object",
                        "description": "Set build-time variables.",
                        "additionalProperties": {
                            "type": "string"
                        }
                    },
                    "no-cache": {
                        "type": "boolean",
                        "description": "Do not use cache when building the image"
                    },
                    "quiet": {
                        "type": "boolean",
                        "description": "Suppress the build output and print image ID on success"
                    },
                    "cpu-shares": {
                        "type": "integer",
                        "description": "CPU shares (relative weight)",
                        "minimum": 0,
                        "maximum": 1024
                    },
                    "memory": {
                        "type": "string",
                        "description": "Memory limit"
                    }
                },
                "required": [
                    "tag",
                    "path",
                    "file"
                ],
                "additionalProperties": False
            },
        },
        "additionalProperties": False
    }
