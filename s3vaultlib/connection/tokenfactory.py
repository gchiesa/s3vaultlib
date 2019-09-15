#!/usr/bin/env python
import json
import logging
import os
import uuid
from copy import deepcopy
from datetime import datetime
from stat import S_IRUSR, S_IWUSR

import pyboto3
import pytz
from botocore.client import Config
from dateutil import parser

from s3vaultlib import __application__
from s3vaultlib.connection.connectionfactory import ConnectionFactory
from s3vaultlib.metadata.factory import MetadataFactory
from .defaults import DEFAULT_TOKEN_FILENAME

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class TokenFactoryException(Exception):
    pass


class TokenFactory(object):
    TOKEN_FILENAME = DEFAULT_TOKEN_FILENAME

    def __init__(self, role_name=None, role_arn=None, external_id=None, connection_factory=None, is_ec2=False):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._role_name = role_name
        self._role_arn = role_arn
        self._external_id = external_id
        self._client = None
        self._connection_factory = connection_factory
        if not self._connection_factory:
            self._connection_factory = ConnectionFactory(config=Config(signature_version='s3v4'), is_ec2=is_ec2)

    @property
    def role_arn(self):
        if not self._role_arn:
            self._role_arn = self._get_role_arn()
        return self._role_arn

    def _get_role_arn(self):
        metadata = MetadataFactory().get_instance(is_ec2=self._connection_factory.is_ec2,
                                                  session_info=self._connection_factory.session_info)
        if not self._role_arn and not self._role_name:
            raise TokenFactoryException('TokenFactory requires either role name or role arn to perform the action.')
        if self._role_arn:
            return self._role_arn
        return 'arn:aws:iam::{account_id}:role/{role_name}'.format(account_id=metadata.account_id,
                                                                   role_name=self._role_name)

    def generate_token(self):
        client = self._connection_factory.client('sts')  # type: pyboto3.sts
        role_args = {
            'RoleArn': self.role_arn,
            'RoleSessionName': 's3vault_{}'.format(str(uuid.uuid4()).replace('-', '')),
        }
        if self._external_id:
            role_args['ExternalId'] = self._external_id
        response = None
        try:
            response = client.assume_role(**role_args)
            token_dict = deepcopy(response.get('Credentials', {}))
        except Exception as e:
            self.logger.error('Error while assuming role with info: {i}. Type: {t}. Error: '
                              '{e}'.format(i=role_args, t=str(type(e)), e=str(e)))
            raise TokenFactoryException(e)

        # convert the date to string
        token_dict['Expiration'] = str(token_dict['Expiration'])
        token_dict['Region'] = self._connection_factory.region
        self._save_token(token_dict)

    def _save_token(self, token_dict):
        with open(os.path.expanduser(self.TOKEN_FILENAME), 'wb') as f_token:
            f_token.write(json.dumps(token_dict).encode())
        os.chmod(os.path.expanduser(self.TOKEN_FILENAME), S_IRUSR | S_IWUSR)

    def _read_token(self):
        if not os.path.exists(os.path.expanduser(self.TOKEN_FILENAME)):
            return None
        try:
            with open(os.path.expanduser(self.TOKEN_FILENAME), 'rb') as f_token:
                data = f_token.read()
                token_dict = json.loads(data.decode())
        except ValueError:
            self.logger.error('Invalid token file: {f}'.format(f=os.path.expanduser(self.TOKEN_FILENAME)))
            return None
        # convert the date
        token_dict['Expiration'] = parser.parse(token_dict['Expiration'])
        return token_dict

    @staticmethod
    def _is_valid_token(token_dict):
        return datetime.now(tz=pytz.utc) < token_dict['Expiration']

    def has_token(self):
        token_dict = self._read_token()
        if not token_dict:
            return False

        if not self._is_valid_token(token_dict):
            self.logger.warning('Token is expired')
            return False
        return True

    @property
    def token(self):
        if not self.has_token():
            return None
        return self._read_token()
