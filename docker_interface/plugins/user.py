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

import pwd
import grp
import os
import subprocess
import tempfile
import uuid

from .base import Plugin, SubstitutionPlugin
from .run import RunConfigurationPlugin
from .. import util


class UserPlugin(Plugin):
    """
    Share the host user id and group id with the container.

    The plugin provides the following additional variables for substitution:

    * :code:`user/name`: Name of the user on the host.
    * :code:`user/uid`: User id of the user on the host.
    * :code:`group/name`: Name of the user group on the host.
    * :code:`group/gid`: Group id of the user group on the host.
    """
    COMMANDS = ['run']
    ORDER = 510
    SCHEMA = {
        "properties": {
            "run": {
                "properties": {
                    "user": util.get_value(
                        RunConfigurationPlugin.SCHEMA, '/properties/run/properties/user')
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    def __init__(self):
        super(UserPlugin, self).__init__()
        self.tempdir = None

    def add_arguments(self, parser):
        self.add_argument(parser, '/run/user')

    def get_user_group(self, user=None, group=None):
        """
        Get the user and group information.

        Parameters
        ----------
        user : str
            User name or user id (default is the `os.getuid()`).
        group : str
            Group name or group id (default is the group of `user`).

        Returns
        -------
        user : pwd.struct_passwd
            User object.
        group : grp.struct_group
            Group object.
        """
        user = user or os.getuid()
        # Convert the information we have obtained to a user object
        try:
            try:
                user = pwd.getpwuid(int(user))
            except ValueError:
                user = pwd.getpwnam(user)
        except KeyError as ex:  # pragma: no cover
            self.logger.fatal("could not resolve user: %s", ex)
            raise

        # Get the group
        group = group or user.pw_gid
        try:
            try:
                group = grp.getgrgid(int(group))
            except ValueError:
                group = grp.getgrnam(group)
        except KeyError as ex:  # pragma: no cover
            self.logger.fatal("could not resolve group:%s", ex)
            raise

        return user, group

    def apply(self, configuration, schema, args):
        # Do not call the super class because we want to do something more sophisticated with the
        # arguments
        user, group = self.get_user_group(*(args.user or '').split(':'))
        SubstitutionPlugin.VARIABLES['user'] = {
            'uid': user.pw_uid,
            'name': user.pw_name,
        }
        SubstitutionPlugin.VARIABLES['group'] = {
            'gid': group.gr_gid,
            'name': group.gr_name,
        }
        util.set_value(configuration, '/run/user', "${user/uid}:${group/gid}")

        # Create a temporary directory and copy the group and passwd files
        if configuration['dry-run']:
            self.logger.warning("cannot mount /etc/passwd and /etc/groups during dry-run")
        else:
            self.tempdir = tempfile.TemporaryDirectory(dir='/tmp')
            name = uuid.uuid4().hex
            # Create a docker image
            image = util.get_value(configuration, '/run/image')
            image = SubstitutionPlugin.substitute_variables(configuration, image, '/run')
            status = subprocess.call([configuration['docker'], 'create', '--name', name, image, 'sh'])
            if status:
                raise RuntimeError(
                    "Could not create container from image '%s'. Did you run `di build`?" % image)
            # Copy out the passwd and group files, mount them, and append the necessary information
            for filename in ['passwd', 'group']:
                path = os.path.join(self.tempdir.name, filename)
                subprocess.check_call([
                    configuration['docker'], 'cp', '%s:/etc/%s' % (name, filename), path])
                util.set_default(configuration, '/run/mount', []).append({
                    'type': 'bind',
                    'source': path,
                    'destination': '/etc/%s' % filename
                })
                with open(path, 'a') as fp:
                    variables = {
                        'user': user.pw_name,
                        'uid': user.pw_uid,
                        'group': group.gr_name,
                        'gid': group.gr_gid
                    }
                    if filename == 'passwd':
                        line = "%(user)s:x:%(uid)d:%(gid)d:%(user)s:/%(user)s:/bin/sh\n" % variables
                    else:
                        line = "%(group)s:x:%(gid)d:%(user)s\n" % variables
                    fp.write(line)
                assert os.path.isfile(path)

            # Destroy the container
            subprocess.check_call(['docker', 'rm', name])

        return configuration

    def cleanup(self):
        if self.tempdir:
            self.tempdir.cleanup()
