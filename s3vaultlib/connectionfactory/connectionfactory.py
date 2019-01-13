#!/usr/bin/env python
import logging
from copy import deepcopy

import boto3

from .. import __application__
from ..ec2metadata import EC2Metadata
from ..tokenfactory import TokenFactory

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
    def __init__(self, region=None, endpoint=None, **params):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._region = region
        self._endpoint = endpoint
        self._params = params

    def client(self, resource):
        """Returns a client connection"""
        return self._connection('client', resource)

    def _connection(self, conn_type=None, resource=None):
        """Allocate a connection"""
        params = deepcopy(self._params)
        profile = params.pop('profile_name', None)
        token = params.pop('token', None)

        if not self._region:
            self._region = EC2Metadata().region

        session_params = {'profile_name': profile}
        if token:
            self.logger.debug('Connection will use session token: {f}'.format(f=TokenFactory.TOKEN_FILENAME))
            session_params = {'aws_access_key_id': token['AccessKeyId'],
                              'aws_secret_access_key': token['SecretAccessKey'],
                              'aws_session_token': token['SessionToken']
                              }

        if conn_type not in ['both', 'resource', 'client']:
            raise ValueError('connection: {c} not supported'.format(c=conn_type))

        if conn_type == 'resource':
            resource = boto3.session.Session(**session_params).resource(resource,
                                                                        region_name=self._region,
                                                                        endpoint_url=self._endpoint,
                                                                        **params)
            return resource
        elif conn_type == 'client':
            client = boto3.session.Session(**session_params).client(resource,
                                                                    region_name=self._region,
                                                                    endpoint_url=self._endpoint,
                                                                    **params)
            return client
        else:
            client = boto3.session.Session(**session_params).client(resource,
                                                                    region_name=self._region,
                                                                    endpoint_url=self._endpoint,
                                                                    **params)
            resource = boto3.session.Session(**session_params).resource(resource,
                                                                        region_name=self._region,
                                                                        endpoint_url=self._endpoint,
                                                                        **params)
            return client, resource
