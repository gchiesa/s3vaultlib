#!/usr/bin/env python
import logging

import yaml
from yaml.scanner import ScannerError

from kmsresolver import KMSResolver
from . import __application__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class ConfigException(Exception):
    pass


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


class ConfigManager(object):
    def __init__(self, config_file):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._config_file = config_file
        self.vault = None
        self.roles = []
        self._role_paths = []

    def get_all_path(self):
        return self._role_paths

    def load_config(self):
        data = {}
        try:
            with open(self._config_file, 'r') as fin:
                data = yaml.load(fin.read())
        except ScannerError as e:
            self.logger.error('Unable to load config file. Error is: {}'.format(str(e)))

        if not data.get('s3vaultlib', None):
            raise ConfigException('No s3vaultlib config section in the file')

        try:
            self.load_vault(data['s3vaultlib'])
        except ConfigException as e:
            raise

        try:
            self.load_roles(data['s3vaultlib'])
        except ConfigException:
            raise
        return self

    def load_vault(self, s3vault_configdata):
        if not s3vault_configdata.get('vault', {}).get('bucket', None):
            raise ConfigException('No bucket configured for vault')
        self.vault = dict(bucket=s3vault_configdata['vault']['bucket'])

    def load_roles(self, s3vault_configdata=None):
        if not (s3vault_configdata.get('roles', None) and len(s3vault_configdata.get('roles', []))):
            raise ConfigException('No roles configured')

        for elem in s3vault_configdata['roles']:
            self.roles.append(self.parse_role_config(elem))

    def parse_role_config(self, role_config):
        if not role_config.get('name', ''):
            raise ConfigException('No role name provided for config: {}'.format(role_config))

        role = Role(role_config['name'], config_obj=self)
        if not role_config.get('path', []):
            role.path = role.name
        else:
            role.path = role_config['path']
        if not role.is_path_all():
            self._role_paths.extend(role.path)

        if not role_config.get('privileges', []):
            raise ConfigException('Privileges not set for role: {}'.format(role.name))
        role.privileges = role_config['privileges']

        if not role_config.get('kms_alias', ''):
            role.kms_alias = role.name
        else:
            role.kms_alias = role_config['kms_alias']

        if role_config.get('managed_policies', []):
            role.managed_policies = role_config['managed_policies']
        return role

    @property
    def path_all(self):
        return self._role_paths


