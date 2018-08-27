#!/usr/bin/env python
import logging
from ..fixtures import s3 as s3fixtures

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class S3Mock(object):
    def __init__(self, mock_id='test_name'):
        self.mock_id = mock_id

    def head_object(self, **kwargs):
        return s3fixtures.S3_OBJECTS[self.mock_id]['head_object']

    def get_object(self, **kwargs):
        return s3fixtures.S3_OBJECTS[self.mock_id]['get_object']

    def list_objects_v2(self, **kwargs):
        return s3fixtures.S3_OBJECTS[self.mock_id]['list_objects_v2']

    def expect_body(self):
        return s3fixtures.S3_OBJECTS[self.mock_id]['_expect_body']
