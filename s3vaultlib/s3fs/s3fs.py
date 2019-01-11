#!/usr/bin/env python
import logging
import os
from io import BytesIO

from .s3fsobject import S3FsObject, S3FsObjectException
from .. import __application__
from ..connectionfactory import ConnectionFactory

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
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
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

    def put_object(self, name, content, encryption_key_arn, force_dot_file=False):
        """
        Put an object in the S3 path by encrypting it with SSE

        :param name: object name
        :param content: content of the object
        :param encryption_key_arn: key arn to use for encryption
        :param force_dot_file: if enabled it disable the check with dot in the file
        :return: the created s3object
        :rtype: S3FsObject
        """
        if os.environ.get('S3VAULTLIB_FORCE_DOT_FILE', 'false').lower() == 'true':
            force_dot_file = True

        if '.' in name and not force_dot_file:
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
