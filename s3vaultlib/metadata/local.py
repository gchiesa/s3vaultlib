#!/usr/bin/env python
import logging
from .base import MetadataBase
from s3vaultlib import __application__
import boto3

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class LocalMetadataException(Exception):
    pass


class LocalMetadata(MetadataBase):
    def __init__(self, session_info=None):
        super(LocalMetadata, self).__init__(session_info)

        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._client = self._session.client('sts')
        """ :type : pyboto3.sts """

    @property
    def account_id(self):
        try:
            response = self._client.get_caller_identity()
            _id = response['Account']
        except Exception as e:
            self.logger.error('Error while retrieving account_id.')
            raise
        return _id

    @property
    def region(self):
        self.logger.debug('Using region from profile (if available) or via command line argument')
        return None

    @property
    def role(self):
        raise LocalMetadataException('Not able to retrieve role from local metadata')

    @property
    def instance_id(self):
        raise LocalMetadataException('Not able to retrieve role instance_id from local metadata')
