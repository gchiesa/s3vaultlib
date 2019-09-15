#!/usr/bin/env python
import logging
from copy import deepcopy

import boto3

from s3vaultlib import __application__
from s3vaultlib.connection.defaults import DEFAULT_TOKEN_FILENAME
from s3vaultlib.metadata.factory import MetadataFactory

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class ConnectionFactory(object):
    """
    Object that allocate connection by supporting also connection profile and extended paramaters
    """

    def __init__(self, region=None, endpoint=None, is_ec2=False, **params):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self.region = region
        self._endpoint = endpoint
        self._is_ec2 = is_ec2
        self._params = params
        self.session_info = None

    @property
    def is_ec2(self):
        return self._is_ec2

    def client(self, resource):
        """Returns a client connection"""
        return self._connection('client', resource)

    def _get_identity_arg(self, session):
        client = session.client('sts')
        """ :type : pyboto3.sts """
        try:
            response = client.get_caller_identity()
            arn = response['Arn']
        except Exception as e:
            self.logger.error('Error while retrieving identity arn')
            return 'n/a'
        return arn

    def _connection(self, conn_type=None, resource=None):
        """Allocate a connection"""
        params = deepcopy(self._params)
        profile = params.pop('profile_name', None)
        token = params.pop('token', None)

        self.session_info = {'profile_name': profile}
        if token:
            self.logger.debug('Connection will use session token: {f}'.format(f=DEFAULT_TOKEN_FILENAME))
            self.session_info = {'aws_access_key_id': token['AccessKeyId'],
                                 'aws_secret_access_key': token['SecretAccessKey'],
                                 'aws_session_token': token['SessionToken'],
                                 'region_name': token['Region']
                                 }

        if conn_type not in ['both', 'resource', 'client']:
            raise ValueError('connection: {c} not supported'.format(c=conn_type))

        session = boto3.session.Session(**self.session_info)
        self.logger.info('Using identity arn: {a}'.format(a=self._get_identity_arg(session)))

        if not self.region:
            metadata = MetadataFactory().get_instance(self._is_ec2, session_info=self.session_info)
            self.region = metadata.region

        if conn_type == 'resource':
            resource = session.resource(resource,
                                        region_name=self.region,
                                        endpoint_url=self._endpoint,
                                        **params)
            return resource
        elif conn_type == 'client':
            client = session.client(resource,
                                    region_name=self.region,
                                    endpoint_url=self._endpoint,
                                    **params)
            return client
        else:
            client = session.client(resource,
                                    region_name=self.region,
                                    endpoint_url=self._endpoint,
                                    **params)
            resource = session.resource(resource,
                                        region_name=self.region,
                                        endpoint_url=self._endpoint,
                                        **params)
            return client, resource
