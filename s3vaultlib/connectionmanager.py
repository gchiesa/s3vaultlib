#!/usr/bin/env python

"""Foobar.py: Description of what foobar does."""
import boto3

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def _boto3_conn(conn_type=None, resource=None, region=None, endpoint=None, **params):
    profile = params.pop('profile_name', None)

    if conn_type not in ['both', 'resource', 'client']:
        raise ValueError('There is an issue in the calling code. You '
                         'must specify either both, resource, or client to '
                         'the conn_type parameter in the boto3_conn function '
                         'call')

    if conn_type == 'resource':
        resource = boto3.session.Session(profile_name=profile).resource(resource, region_name=region, endpoint_url=endpoint, **params)
        return resource
    elif conn_type == 'client':
        client = boto3.session.Session(profile_name=profile).client(resource, region_name=region, endpoint_url=endpoint, **params)
        return client
    else:
        client = boto3.session.Session(profile_name=profile).client(resource, region_name=region, endpoint_url=endpoint, **params)
        resource = boto3.session.Session(profile_name=profile).resource(resource, region_name=region, endpoint_url=endpoint, **params)
        return client, resource


class ConnectionManager(object):
    def __init__(self, region=None, endpoint=None, **params):
        self._region = region
        self._endpoint = endpoint
        self._params = params

    def client(self, resource):
        return _boto3_conn('client', resource, self._region, self._endpoint, **self._params)

