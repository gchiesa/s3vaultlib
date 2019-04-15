#!/usr/bin/env python
import json
import logging
import os
from collections import OrderedDict

from jinja2 import Environment, FileSystemLoader
from string_utils import snake_case_to_camel

from .. import __application__
from ..configmanager import ConfigManager

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')


def cloudformation_sanitize_string(string):
    string_new = snake_case_to_camel(string.replace('-', '_')).replace('_', '')
    return string_new


def cloudformation_prettyprint(json_string):
    data = json.loads(json_string, object_pairs_hook=OrderedDict)
    return json.dumps(data, indent=4, separators=(',', ': '))


class PolicyManager(object):
    def __init__(self, config_manager):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._config_manager = config_manager  # type: ConfigManager
        self._j2env = Environment(loader=FileSystemLoader(os.path.join(BASE_PATH, '_resources', 'templates')),
                                  trim_blocks=True, autoescape=False)
        self._j2env.filters['cfsanitize'] = cloudformation_sanitize_string
        self._policy_variables = None
        self._connection_factory = None
        self._account_id = ''

    def get_policy_variables(self):
        if not self._policy_variables:
            self._policy_variables = self._load_vars()
        return self._policy_variables

    def _generate_bucket(self):
        pass

    def _generate_roles(self):
        template = self._j2env.get_template('roles.j2')
        cf_data = template.render(self.get_policy_variables())
        return cf_data

    def _generate_kms(self):
        template = self._j2env.get_template('kms.j2')
        cf_data = template.render(self.get_policy_variables())
        return cf_data

    def _generate_bucket_policy(self):
        template = self._j2env.get_template('bucket_policy.j2')
        cf_data = template.render(self.get_policy_variables())
        return cf_data

    def _generate_outputs(self):
        template = self._j2env.get_template('outputs.j2')
        cf_data = template.render(self.get_policy_variables())
        return cf_data

    def _load_vars(self):
        self._data = dict(vault=dict(bucket=self._config_manager.vault['bucket'],
                                     path_all=self._config_manager.path_all,
                                     roles=self._config_manager.roles))
        if self._connection_factory:
            self._data['vault']['roles'] = [role.with_connection_factory(self._connection_factory) for role in
                                           self._config_manager.roles]
        return self._data

    def with_connection_factory(self, connection_factory):
        self._connection_factory = connection_factory
        return self

    def with_account_id(self, account_id):
        self._account_id = account_id
        return self

    def generate_cloudformation(self):
        template = self._j2env.get_template('cf_template.j2')
        variables = dict(roles=self._generate_roles(),
                         bucket_policy=self._generate_bucket_policy(),
                         kms=self._generate_kms(),
                         outputs=self._generate_outputs())
        rendered = template.render(variables)
        self.logger.debug('generated code: \n{}'.format(rendered))
        return cloudformation_prettyprint(rendered)
