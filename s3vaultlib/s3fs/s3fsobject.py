#!/usr/bin/env python
import copy
import json
import logging
import os

from dpath.util import merge

from .. import __application__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class S3FsObjectException(Exception):
    pass


class S3FsObject(object):
    """
    Implement the S3FsObject, an abstraction around a S3 file with SSE encryption
    """
    def __init__(self, data, bucket, path, fs):
        """

        :param data: json metadata from the file
        :param bucket: bucket
        :param path: path
        :param fs: s3 cient
        """
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._data = data
        self._header = {}
        self._bucket = bucket
        self._path = path
        self._raw = ''
        self._is_json = False
        self._fs = fs
        """ :type : pyboto3.s3 """
        if not self._data.get('Key'):
            raise S3FsObjectException('Not a valid object')
        self.name = self._data['Key'].rpartition('/')[-1]

    @property
    def kms_arn(self):
        """
        Return the KMS ARN used to encrypt the object

        :return: KMS ARN
        :rtype: basestring
        """
        return self._header.get('SSEKMSKeyId', '')

    @property
    def is_encrypted(self):
        """
        Return true if the object is encrypted

        :return: True or False
        :rtype: bool
        """
        if self.kms_arn:
            return True
        return False

    @property
    def metadata(self):
        """
        Return the metadata associated with the object (file metadata)

        :return: medatata
        :rtype: dict
        """
        if not self._header:
            self._load_content()
        metadata = copy.deepcopy(self._header)
        return metadata

    def _load_content(self):
        """
        Load the content of the file pointed by S3FsObject

        :return: content of the file
        """
        object_path = os.path.join(self._path, self.name)
        try:
            self._header = self._fs.head_object(Bucket=self._bucket, Key=object_path)
        except Exception:
            self.logger.exception('Exception while fetching header for key: {k}'.format(k=object_path))
            raise

        response = self._fs.get_object(Bucket=self._bucket, Key=object_path)
        if not response.get('Body'):
            raise S3FsObjectException('Unable to read the file content for key: {k}'.format(k=object_path))
        self._raw = bytes(response['Body'].read())
        return self._raw

    @staticmethod
    def is_json(data):
        """
        Return True if the content is a valid json

        :param data: content to evaluate
        :return: True or False
        :rtype: bool
        """
        try:
            json.loads(data)
        except ValueError:
            return False
        return True

    def __getitem__(self, key):
        """
        Overrides the getitem method

        :param key:
        :return:
        """
        if not self._raw:
            self._load_content()

        if not self.is_json(self._raw):
            raise KeyError(key)

        json_data = json.loads(self._raw)
        return self._get_value(json_data, key)

    @staticmethod
    def _set_value(d, path, value):
        levels = path.split('.')
        leaf_key = levels.pop()
        tmp_dict = {leaf_key: value}
        for key in reversed(levels):
            tmp_dict = {key: tmp_dict}
        merge(d, tmp_dict)
        return d

    @staticmethod
    def _get_value(d, path):
        k, _, rest = path.partition('.')
        if not rest:
            return d[k]
        if not isinstance(d[k], dict):
            raise KeyError('{} is a leaf value, not a dict'.format(d[k]))
        return S3FsObject._get_value(d[k], rest)

    def __setitem__(self, key, value):
        """
        Overrides the setitem method

        :param key:
        :param value:
        :return:
        """
        if not self._raw:
            self._load_content()

        if not self.is_json(self._raw):
            raise KeyError(key)

        json_data = json.loads(self._raw)
        # if the key contains . separator then we assume the key is a nested key and we allocate the entire path
        json_data = self._set_value(json_data, key, value)
        self._raw = json.dumps(json_data)

    def __getattr__(self, item):
        """
        Override the setattr method

        :param item:
        :return:
        """
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __str__(self):
        """
        Override the str method

        :return:
        """
        if not self._raw:
            self._load_content()
        return self._raw

    def raw(self):
        if not self._raw:
            self._load_content()
        return self._raw


