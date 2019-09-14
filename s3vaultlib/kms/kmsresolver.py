#!/usr/bin/env python
import logging

from s3vaultlib import __application__
from s3vaultlib.metadata.factory import MetadataFactory
from s3vaultlib.connection.connectionfactory import ConnectionFactory

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class KMSResolverException(Exception):
    pass


class KMSResolver(object):
    """
    Object that resolves the KMS key associated to a role, or
    load a keyarn with a specified alias
    """

    def __init__(self, connection_factory, keyalias='', role_name=''):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))

        self._connection_factory = connection_factory
        """ :type : s3vaultlib.connection.connectionfactory.ConnectionFactory """
        self._keyalias = keyalias
        self._role = role_name
        self._kms = self._connection_factory.client('kms')
        """ :type : pyboto3.kms """

    def _get_key_from_alias(self, alias):
        key_id = 'alias/{a}'.format(a=alias.rpartition('alias/')[-1])
        key_data = self._kms.describe_key(KeyId=key_id)
        if not key_data.get('KeyMetadata'):
            return ''
        return key_data['KeyMetadata'].get('Arn')

    def retrieve_key_arn(self):
        """
        Return the KMS arn of a key

        :return: key arn
        :rtype: basestring
        """
        key_arn = ''
        if self._keyalias:
            key_arn = self._get_key_from_alias(self._keyalias)

        if key_arn:
            return key_arn

        if self._role:
            key_arn = self._get_key_from_alias(self._role)

        if key_arn:
            return key_arn

        metadata = MetadataFactory().get_instance(is_ec2=self._connection_factory.is_ec2,
                                                  session_info=self._connection_factory.session_info)
        try:
            role = metadata.role
        except Exception as e:
            self.logger.error('Error while retrieving role. Type: {t}. Error: {e}'.format(t=str(type(e)), e=str(e)))
            raise

        key_arn = self._get_key_from_alias(role)
        if not key_arn:
            raise KMSResolverException('Unable to resolve the key from role: {r}'.format(r=role))
        return key_arn
