#!/usr/bin/env python

"""Foobar.py: Description of what foobar does."""
import sys
import jinja2
import logging
import argparse
from .connectionmanager import ConnectionManager
from .s3fs import S3Fs, S3FsObjectException
from .kmsresolver import KMSResolver
from botocore.client import Config
from . import __version__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class TemplateRenderer(object):
    def __init__(self, template_file, s3fs):
        self._template_file = template_file
        self._s3fs = s3fs
        """ :type : S3Fs """

    def render(self, **kwargs):
        with open(self._template_file, 'rb') as tpl_file:
            tpl_data = tpl_file.read()
        template = jinja2.Template(tpl_data)
        variables = {obj.name: obj for obj in self._s3fs.objects}
        result = template.render(**variables)
        return result


class S3Vault(object):
    def __init__(self, bucket, path, connection_manager=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._bucket = bucket
        self._path = path
        self._connection_manager = connection_manager
        if not self._connection_manager:
            self._connection_manager = ConnectionManager(config=Config(signature_version='s3v4'))

    def put_file(self, src, dest, encryption_key_arn='', key_alias='', role_name=''):
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        kms_resolver = KMSResolver(self._connection_manager, keyalias=key_alias, role_name=role_name)
        key_arn = encryption_key_arn
        if not encryption_key_arn:
            key_arn = kms_resolver.retrieve_key_arn()
        with open(src, 'rb') as src_file:
            s3fsobj = s3fs.put_object(dest, src_file.read(), key_arn)
            """ :type : S3FsObject """
        return s3fsobj.metadata

    def get_file(self, name):
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        s3fsobject = s3fs.get_object(name)
        return str(s3fsobject)

    def render_template(self, template_file, **kwargs):
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        template_renderer = TemplateRenderer(template_file, s3fs)
        return template_renderer.render()

    def create_config_property(self, configfile, encryption_key_arn='', key_alias='', role_name=''):
        self.logger.info('Creating new config file: {c}'.format(c=configfile))
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        kms_resolver = KMSResolver(self._connection_manager, keyalias=key_alias, role_name=role_name)
        key_arn = encryption_key_arn
        if not encryption_key_arn:
            key_arn = kms_resolver.retrieve_key_arn()
        s3fsobject = s3fs.put_object(configfile, '{}', key_arn)
        return s3fsobject

    def set_property(self, configfile, key, value, encryption_key_arn='', key_alias='', role_name=''):
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        try:
            s3fsobject = s3fs.get_object(configfile)
        except S3FsObjectException:
            s3fsobject = self.create_config_property(configfile, encryption_key_arn, key_alias, role_name)
        s3fsobject[key] = value
        s3fsobj = s3fs.update_s3fsobject(s3fsobject)
        return s3fsobj.metadata

    def get_property(self, configfile, key):
        s3fs = S3Fs(self._connection_manager, self._bucket, self._path)
        try:
            s3fsobject = s3fs.get_object(configfile)
        except:
            self.logger.exception('No configuration with name: {c} found'.format(c=configfile))
            raise
        return s3fsobject[key]


def check_args():
    parser = argparse.ArgumentParser(prog='s3vaultcli', description='s3vaultcli', version=__version__)
    parser.add_argument('-b', '--bucket', dest='bucket', required=True,
                        help='Bucket to use for S3Vault')
    parser.add_argument('-p', '--path', dest='path', required=True,
                        help='Path to use in the bucket')
    parser.add_argument('-k', '--kms-alias', dest='kms_alias', required=False,
                        help='Key alias to use to decrypt data')
    parser.add_argument('-L', '--log-level', dest='log_level', required=False,
                        help='Log level to set',
                        choices=['debug', 'info', 'warning', 'error'],
                        default='info')
    parser.add_argument('--profile', dest='profile', required=False,
                        help='AWS profile to use')
    parser.add_argument('--region', dest='region', required=False,
                        help='AWS region to use')

    subparsers = parser.add_subparsers(dest='command')
    template = subparsers.add_parser('template', help='Expand a template file based on a S3Vault')
    template.add_argument('-t', '--template', dest='template', required=True,
                          help='Template to expand from s3vault path',
                          type=argparse.FileType('rb'))
    template.add_argument('-d', '--dest', dest='dest', required=True,
                          help='Destination file',
                          type=argparse.FileType('wb'))

    pushfile = subparsers.add_parser('push', help='Push a file in the S3Vault')
    pushfile.add_argument('-s', '--src', dest='src', required=True,
                          help='Source file to upload',
                          type=argparse.FileType('rb'))
    pushfile.add_argument('-d', '--dest', dest='dest', required=True,
                          help='Destination name')

    setproperty = subparsers.add_parser('configset', help='Set a property in a configuration file in the S3Vault')
    setproperty.add_argument('-c', '--config', dest='config', required=True,
                             help='Configuration file to manage')
    setproperty.add_argument('-K', '--key', dest='key', required=True,
                             help='Key to set')
    setproperty.add_argument('-V', '--value', dest='value', required=True,
                             help='Value to set')
    return parser.parse_args()


def configure_logging(level):
    formatter = '[%(asctime)s] [%(levelname)s] [%(name)s] [%(message)s]'
    logging.basicConfig(level=logging.getLevelName(level.upper()),
                        format=formatter)


def main():
    args = check_args()
    configure_logging(args.log_level)
    logger = logging.getLogger(__name__)

    conn_manager = None
    if args.profile:
        conn_manager = ConnectionManager(region=args.region, profile=args.profile)

    s3vault = S3Vault(args.bucket, args.path, connection_manager=conn_manager)

    if args.command == 'template':
        try:
            args.dest.write(s3vault.render_template(args.template.name))
        except Exception as e:
            logger.exception('Error while expanding the template. Exiting')
            sys.exit(1)
    elif args.command == 'push':
        try:
            logger.info(args.src.name)
            metadata = s3vault.put_file(src=args.src.name,
                                        dest=args.dest,
                                        key_alias=args.kms_alias)
            logger.debug('s3fsobject metadata: {d}'.format(d=metadata))
        except Exception as e:
            logger.exception('Error while pushing file. Error: {t} / {e}'.format(t=str(type(e)),
                                                                                 e=str(e)))
            sys.exit(1)
    elif args.command == 'configset':
        try:
            metadata = s3vault.set_property(configfile=args.config,
                                            key=args.key,
                                            value=args.value,
                                            key_alias=args.kms_alias)
            logger.debug('s3fsobject metadata: {d}'.format(d=metadata))
        except Exception as e:
            logger.exception('Error while setting property. Error: {t} / {e}'.format(t=str(type(e)),
                                                                                     e=str(e)))
    else:
        logger.error('Command not available')
        sys.exit(1)


if __name__ == '__main__':
    main()
