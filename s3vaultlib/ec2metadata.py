#!/usr/bin/env python
import requests
import logging

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
        self.logger = logging.getLogger(self.__class__.__name__)
        self._endpoint = endpoint
        self._version = version
        self._uri = 'http://{e}/{v}'.format(e=endpoint, v=version)

    def _get_data(self, url_path):
        """
        Query the metadata
        """
        url = '{b}/{p}'.format(b=self._uri, p=url_path)
        try:
            response = requests.get(url)
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
