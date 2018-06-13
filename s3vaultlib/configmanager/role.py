#!/usr/bin/env python
import logging

from .. import __application__
from ..kmsresolver import KMSResolver

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class RoleException(Exception):
    pass


class Role(object):
    SUPPORTED_PRIVILEGES = ('read', 'write')

    def __init__(self, name, config_obj):
        """
        Role Object

        :param name: role name
        :param config_obj: ConfigManager object
        :type config_obj: ConfigManager
        """
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._name = name
        self._priv = []
        self._path = []
        self._config_obj = config_obj
        """ :type : S3VaultConfig """
        self._kms_alias = ''
        self._kms_arn = None
        self._managed_policies = []
        self._connection_factory = None
        self._arn = None

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        if self.is_path_all():
            return self._config_obj.get_all_path()
        else:
            return self._path

    @path.setter
    def path(self, path):
        if isinstance(path, list):
            self._path = path
        else:
            self._path = [path]
        self._path = list(map(self._path_sanitizer, self._path))

    @staticmethod
    def _path_sanitizer(path):
        if path[-1] == '/':
            return path[:-1]
        return path

    @property
    def privileges(self):
        return self._priv

    @privileges.setter
    def privileges(self, privileges):
        priv = []
        if not isinstance(privileges, list):
            priv.append(privileges)
        else:
            priv = privileges
        if any([p not in self.SUPPORTED_PRIVILEGES for p in priv]):
            raise RoleException('Privileges: {p} contains not supported keywords. Allowed: '
                                '{a}'.format(p=privileges, a=self.SUPPORTED_PRIVILEGES))
        self._priv = priv

    @property
    def kms_alias(self):
        return self._kms_alias

    @kms_alias.setter
    def kms_alias(self, kms_alias):
        self._kms_alias = kms_alias

    @property
    def managed_policies(self):
        return self._managed_policies

    @managed_policies.setter
    def managed_policies(self, policy_list):
        self._managed_policies = policy_list

    def is_path_all(self):
        return self._path == ['_all_']

    def with_connection_factory(self, connection_factory):
        self._connection_factory = connection_factory
        return self

    @property
    def kms_arn(self):
        if not self._connection_factory:
            self.logger.warning('Connection factory not instantiated, you may want to use with_connection_factory first')
            return ''
        if not self._kms_arn:
            kms_resolver = KMSResolver(connection_manager=self._connection_factory, keyalias=self.kms_alias)
            self._kms_arn = kms_resolver.retrieve_key_arn()
        return self._kms_arn
