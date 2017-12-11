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
                        "description": "Set build-time variables."
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
                ]
            }
        }
    }
