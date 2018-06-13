#!/usr/bin/env python
from ..ec2metadata import EC2Metadata

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
    def __init__(self, connection_manager, keyalias='', role_name=''):
        self._connmanager = connection_manager
        """ :type : ConnectionManager """
        self._keyalias = keyalias
        self._role = role_name
        self._kms = self._connmanager.client('kms')
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

        role = EC2Metadata().role
        key_arn = self._get_key_from_alias(role)
        if not key_arn:
            raise KMSResolverException('Unable to resolve the key')
        return key_arn

