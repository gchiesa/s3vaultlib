#!/usr/bin/env python
import logging

from .role import Role
from .. import __application__
from ..utils import yaml
from ..utils.yaml import ParserError, ScannerError

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class ConfigException(Exception):
    pass


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
                data = yaml.load_to_string(fin.read())
        except (ParserError, ScannerError) as e:
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
        if not s3vault_configdata.get('vault', None):
            raise ConfigException('Vault section empty')
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

