#!/usr/bin/env python
import logging
import json
import os
from io import BytesIO
from .connectionfactory import ConnectionFactory

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


MAX_S3_RETURNED_OBJECTS = 999


class S3FsException(Exception):
    pass


class S3Fs(object):
    """
    Object that abstracts operation with encrypted objects on S3
    """
    def __init__(self, connection_factory, bucket, path=''):
        """

        :param connection_factory: connection_factory object
        :type connection_factory: ConnectionFactory
        :param bucket: S3 bucket
        :param path: bucket path
        """
        self._connection_factory = connection_factory
        """ :type : ConnectionFactory """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._bucket = bucket
        self._path = path
        self._s3fs_objects = []
        self.fs = self._connection_factory.client('s3')
        """ :type : pyboto3.s3 """

    @staticmethod
    def is_file(s3elem):
        """
        Return true is an s3 json element represents a valid file
        """
        try:
            key = s3elem['Key']
        except KeyError:
            return False
        name = key.rpartition('/')[-1]
        if not name:
            return False
        return True

    @property
    def objects(self):
        """
        Return a list of s3fsobjects
        """
        return self._get_s3fsobjects()

    def _get_s3fsobjects(self, refresh=False):
        """
        load the s3fsobjects from an S3 path
        :param refresh: True to reload the objects
        :return: list of object
        :rtype: list
        """
        if self._s3fs_objects and not refresh:
            return self._s3fs_objects
        response = self.fs.list_objects_v2(Bucket=self._bucket,
                                           Prefix=self._path,
                                           MaxKeys=MAX_S3_RETURNED_OBJECTS)
        if not response.get('Contents'):
            self._s3fs_objects = []
            return self._s3fs_objects

        for elem in response.get('Contents'):
            if self.is_file(elem):
                self._s3fs_objects.append(S3FsObject(elem, self._bucket, self._path, self.fs))
        return self._s3fs_objects

    def get_object(self, name):
        """
        Return a s3fsobject identified by name
        :param name: object name
        :return: s3fsobject
        :rtype: S3FsObject
        """
        s3obj = next(iter([s3fsobj for s3fsobj in self.objects if s3fsobj.name == name]), None)
        if not s3obj:
            raise S3FsObjectException('Object not found')
        return s3obj

    def put_object(self, name, content, encryption_key_arn):
        """
        Put an object in the S3 path by encrypting it with SSE
        :param name: object name
        :param content: content of the object
        :param encryption_key_arn: key arn to use for encryption
        :return: the created s3object
        :rtype: S3FsObject
        """
        if '.' in name:
            raise ValueError('object does not support . (dot) in the name')

        self.logger.info('Adding object: {n}, size: {s}, to bucket: {b}, path: {p}'.format(n=name,
                                                                                           s=len(content),
                                                                                           b=self._bucket,
                                                                                           p=self._path))
        object_body = BytesIO(content)
        self.fs.put_object(Bucket=self._bucket,
                           ServerSideEncryption='aws:kms',
                           Body=object_body,
                           Key=os.path.join(self._path, name),
                           SSEKMSKeyId=encryption_key_arn)
        s3obj = next(iter([s3fsobj for s3fsobj in self._get_s3fsobjects(refresh=True) if s3fsobj.name == name]), None)
        return s3obj

    def update_s3fsobject(self, s3fsobject):
        """
        Update an S3FSObject
        :param s3fsobject: S3FsObject to update
        :type: S3FsObject
        :return: the updated object
        :rtype: S3FsObject
        """
        if not s3fsobject.is_encrypted:
            raise S3FsException('Unable to update unencrypted object')
        return self.put_object(s3fsobject.name, str(s3fsobject), s3fsobject.kms_arn)


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
        self.logger = logging.getLogger(self.__class__.__name__)
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
        return self._data

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
        self._raw = response['Body'].read()
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

    def __getitem__(self, item):
        """
        Overrides the getitem method
        :param item:
        :return:
        """
        if not self._raw:
            self._load_content()

        if not self.is_json(self._raw):
            raise KeyError(item)

        json_data = json.loads(self._raw)
        if json_data.get(item, ''):
            return json_data[item]
        raise KeyError(item)

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
        json_data[key] = value
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
