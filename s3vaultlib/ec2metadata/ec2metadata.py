#!/usr/bin/env python
import json
import logging

import requests

from .. import __application__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class EC2MetadataException(Exception):
    pass


class EC2Metadata(object):
    """
    Object that retrieve metadata from within an EC2 instance
    """
    def __init__(self, endpoint='169.254.169.254', version='latest'):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._endpoint = endpoint
        self._version = version
        self._instance_identity_document = None
        self._uri = 'http://{e}/{v}'.format(e=endpoint, v=version)

    def _get_data(self, url_path):
        """
        Query the metadata
        """
        url = '{b}/{p}'.format(b=self._uri, p=url_path)
        try:
            response = requests.get(url, timeout=5)
        except Exception:
            self.logger.exception('Error while getting metadata')
            raise
        if not response.ok:
            raise EC2MetadataException('Error while reading metadata from path')
        return response.text.strip()

    @property
    def role(self):
        """
        Return the role associated to the instance
        """
        data = self._get_data('meta-data/iam/security-credentials/')
        if not data:
            raise EC2MetadataException('Role not associated')
        return data

    @property
    def account_id(self):
        """
        Return the account_id associated to the instance

        :return: account_id
        :rtype: basestring
        """
        return self._get_instance_identity_document()['accountId']

    @property
    def region(self):
        """
        Return the region associated to the instance

        :return: region
        :rtype: basestring
        """
        return self._get_instance_identity_document()['availabilityZone'][:-1]

    @property
    def instance_id(self):
        """
        Return the instance_id associated to the instance

        :return: instance_id
        :rtype: basestring
        """
        return self._get_instance_identity_document()['instanceId']

    def _get_instance_identity_document(self):
        if not self._instance_identity_document:
            data = self._get_data('dynamic/instance-identity/document')
            if not data:
                raise EC2MetadataException('Unable to retrieve instance identity document')
            self._instance_identity_document = json.loads(data)
        return self._instance_identity_document
