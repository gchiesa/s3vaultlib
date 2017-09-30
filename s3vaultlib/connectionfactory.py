#!/usr/bin/env python
import boto3
import logging
from .ec2metadata import EC2Metadata

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
        self.logger = logging.getLogger(self.__class__.__name__)
        self._region = region
        self._endpoint = endpoint
        self._params = params

    def client(self, resource):
        """Returns a client connection"""
        return self._connection('client', resource)

    def _connection(self, type=None, resource=None):
        """Allocate a connection"""
        profile = self._params.pop('profile_name', None)
        if not self._region:
            self._region = EC2Metadata().region

        if type not in ['both', 'resource', 'client']:
            raise ValueError('connection: {c} not supported'.format(c=type))

        if type == 'resource':
            resource = boto3.session.Session(profile_name=profile).resource(resource,
                                                                            region_name=self._region,
                                                                            endpoint_url=self._endpoint,
                                                                            **self._params)
            return resource
        elif type == 'client':
            client = boto3.session.Session(profile_name=profile).client(resource,
                                                                        region_name=self._region,
                                                                        endpoint_url=self._endpoint,
                                                                        **self._params)
            return client
        else:
            client = boto3.session.Session(profile_name=profile).client(resource,
                                                                        region_name=self._region,
                                                                        endpoint_url=self._endpoint,
                                                                        **self._params)
            resource = boto3.session.Session(profile_name=profile).resource(resource,
                                                                            region_name=self._region,
                                                                            endpoint_url=self._endpoint,
                                                                            **self._params)
            return client, resource
