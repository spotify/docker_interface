import pwd
import grp
import os

from .base import Plugin, SubstitutionPlugin
from .run import RunPlugin
from .. import json_util


class UserPlugin(Plugin):
    """
    Share the host user id and group id with the container.
    """
    COMMANDS = ['run']
    ORDER = 510

    def add_arguments(self, parser):
        self.add_argument(parser, '/run/user', schema=RunPlugin.SCHEMA)

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
        json_util.set_value(configuration, '/run/user', "${user/uid}:${group/gid}")
        return configuration
