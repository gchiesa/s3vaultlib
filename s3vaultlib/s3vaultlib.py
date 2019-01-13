#!/usr/bin/env python
import logging

import six
from botocore.client import Config

from . import __application__
from .connectionfactory import ConnectionFactory
from .kmsresolver import KMSResolver
from .s3fs import S3Fs, S3FsObjectException, S3FsObject
from .templatefile import TemplateFile
from .templaterenderer import TemplateRenderer

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class S3Vault(object):
    """
    Implements a Vault by using S3 as backend and KMS as way to protect the data
    """

    def __init__(self, bucket, path, connection_factory=None):
        """

        :param bucket: bucket
        :param path: path
        :param connection_factory: connection factory
        :type connection_factory: ConnectionFactory
        """
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._bucket = bucket
        self._path = path
        self._connection_manager = connection_factory
        if not self._connection_manager:
            self._connection_manager = ConnectionFactory(config=Config(signature_version='s3v4'))

    def put_file(self, src, dest, encryption_key_arn='', key_alias='', role_name=''):
        """
        Upload a file to the S3Vault

        :param src: source file name
        :param dest: destination file name
        :param encryption_key_arn: KMS Key arn to use
        :param key_alias: KMS Key alias to use
        :param role_name: Role from which resolve the key
        :return: metadata of the uploaded object
        :rtype: dict
        """
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        kms_resolver = KMSResolver(self._connection_manager, keyalias=key_alias, role_name=role_name)
        key_arn = encryption_key_arn
        if not encryption_key_arn:
            key_arn = kms_resolver.retrieve_key_arn()

        if isinstance(src, six.string_types):
            src_file = open(src, 'rb')
        else:
            src_file = src
        s3fsobj = s3fs.put_object(dest, src_file.read(), key_arn)  # type: S3FsObject
        src_file.close()
        return s3fsobj.metadata

    def get_file(self, name):
        """
        Get a file from S3Vault

        :param name: filename
        :return: file content
        :rtype: basestring
        """
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        s3fsobject = s3fs.get_object(name)  # type: S3FsObject
        return s3fsobject.raw()

    def get_file_metadata(self, name):
        """
        Get a file from S3Vault

        :param name: filename
        :return: file content
        :rtype: dict
        """
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        s3fsobject = s3fs.get_object(name)
        return s3fsobject.metadata

    def render_template(self, template_file, **kwargs):
        """
        Renders a template file using the information available in the S3Vault

        :param template_file: file name to use as template
        :param kwargs: additional variables to use in the rendering
        :return: rendered content
        :rtype: basestring
        """
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        tpl = TemplateFile(template_file)
        if tpl.is_raw_copy(s3fs.objects):
            s3fsobject = s3fs.get_object(tpl.get_raw_copy_src())
            data = s3fsobject.raw()
        else:
            template_renderer = TemplateRenderer(tpl.filename, s3fs)
            data = template_renderer.render(**kwargs)
        return data

    def create_config_property(self, configfile, encryption_key_arn='', key_alias='', role_name=''):
        """
        Create a configuration file in the S3Vault

        :param configfile: configuration file name
        :param encryption_key_arn: KMS Arn to use
        :param key_alias: KMS Alias to use
        :param role_name: Role to use to resolve the KMS Key
        :return: s3fsobject
        :rtype: S3FsObject
        """
        self.logger.info('Creating new config file: {c}'.format(c=configfile))
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        kms_resolver = KMSResolver(self._connection_manager, keyalias=key_alias, role_name=role_name)
        key_arn = encryption_key_arn
        if not encryption_key_arn:
            key_arn = kms_resolver.retrieve_key_arn()
        s3fsobject = s3fs.put_object(configfile, '{}', key_arn)
        return s3fsobject

    def set_property(self, configfile, key, value, encryption_key_arn='', key_alias='', role_name=''):
        """
        Set a property in a configuration file in the S3Vault

        :param configfile: configfile name
        :param key: key
        :param value: value
        :param encryption_key_arn: KMS Key to use
        :param key_alias: KMS alias to use
        :param role_name: Role to use to resolve the KMS Key
        :return: metadata of the config file created/updated
        :rtype: basestring
        """
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        try:
            s3fsobject = s3fs.get_object(configfile)
            """ :type: S3FsObject """
        except S3FsObjectException:
            s3fsobject = self.create_config_property(configfile, encryption_key_arn, key_alias, role_name)
        s3fsobject[key] = value
        s3fsobj = s3fs.update_s3fsobject(s3fsobject)
        return s3fsobj.metadata

    def get_property(self, configfile, key):
        """
        Get a configuration property from a config file from the S3Vault

        :param configfile: configuration file
        :param key: key to query
        :return: value of the key
        """
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        try:
            s3fsobject = s3fs.get_object(configfile)
        except:
            self.logger.exception('No configuration with name: {c} found'.format(c=configfile))
            raise
        return s3fsobject[key]

