#!/usr/bin/env python
import argparse
import ast
import copy
import logging
import os
import shutil
import sys
from getpass import getpass

from . import __application__
from . import __version__
from .configmanager import ConfigManager
from .connectionfactory import ConnectionFactory
from .policymanager import PolicyManager
from .s3vaultlib import S3Vault
from .tokenfactory import TokenFactory

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def check_args():
    """
    Check the args from the command line

    :return: args object
    """
    parser = argparse.ArgumentParser(prog='s3vaultcli', description='s3vaultcli', version=__version__)

    parser.add_argument('-L', '--log-level', dest='log_level', required=False,
                        help='Log level to set',
                        choices=['debug', 'info', 'warning', 'error'],
                        default='info')
    parser.add_argument('--profile', dest='profile', required=False,
                        help='AWS profile to use',
                        default=None)
    parser.add_argument('--region', dest='region', required=False,
                        help='AWS region to use',
                        default=None)

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-b', '--bucket', dest='bucket', required=True,
                               help='Bucket to use for S3Vault')
    common_parser.add_argument('-p', '--path', dest='path', required=True,
                               help='Path to use in the bucket')
    kms = common_parser.add_mutually_exclusive_group()
    kms.add_argument('-k', '--kms-alias', dest='kms_alias', required=False,
                     default='',
                     help='Key alias to use to decrypt data')
    kms.add_argument('--kms-arn', dest='kms_arn', required=False,
                     default='',
                     help='Key arn to use to decrypt data')

    subparsers = parser.add_subparsers(dest='command')
    template = subparsers.add_parser('template', help='Expand a template file based on a S3Vault',
                                     parents=[common_parser])
    template.add_argument('-t', '--template', dest='template', required=True,
                          help='Template to expand from s3vault path',
                          type=argparse.FileType('rb'))
    template.add_argument('-d', '--dest', dest='dest', required=True,
                          help='Destination file',
                          type=argparse.FileType('wb'))

    pushfile = subparsers.add_parser('push', help='Push a file in the S3Vault',
                                     parents=[common_parser])
    pushfile.add_argument('-s', '--src', dest='src', required=True,
                          help='Source file to upload',
                          type=argparse.FileType('rb'))
    pushfile.add_argument('-d', '--dest', dest='dest', required=True,
                          help='Destination name')

    setproperty = subparsers.add_parser('configset', help='Set a property in a configuration file in the S3Vault',
                                        parents=[common_parser])
    setproperty.add_argument('-c', '--config', dest='config', required=True,
                             help='Configuration file to manage')
    setproperty.add_argument('-K', '--key', dest='key', required=True,
                             help='Key to set')
    setproperty.add_argument('-V', '--value', dest='value', required=True,
                             help='Value to set')
    setproperty.add_argument('-T', '--type', dest='value_type', required=False,
                             choices=['string', 'list', 'dict'],
                             default='string',
                             help='Data type for the value')
    create_session = subparsers.add_parser('create_session', help='Create a new session with assume role')
    """ :type : argparse.ArgumentParser """
    create_session.add_argument('-r', '--role-name', dest='role_name', required=True,
                                help='Role to assume')
    create_s3vault_config = subparsers.add_parser('create_s3vault_config', help='Create a new s3vault configuration '
                                                                                'file')
    """ :type : argparse.ArgumentParser """
    create_s3vault_config.add_argument('-o', '--output', dest='output_file', required=True,
                                       type=argparse.FileType('wb'),
                                       help='Config file to create')
    cloudformation_generate = subparsers.add_parser('create_cloudformation',
                                                    help='Generate a CloudFormation template from a s3vault '
                                                         'configuration')
    """ :type : argparse.ArgumentParser """
    cloudformation_generate.add_argument('-c', '--config', dest='s3vault_config', required=True,
                                         type=argparse.FileType('rb'),
                                         help='S3vault configuration file')
    cloudformation_generate.add_argument('-o', '--output', dest='output_file', required=True,
                                         type=argparse.FileType('wb'),
                                         help='CloudFormation output file')
    ansible = subparsers.add_parser('ansible_path', help='Resolve the ansible module path')
    return parser.parse_args()


def configure_logging(level):
    """
    Configure the logging level of the tool

    :param level: level to set
    :return:
    """
    formatter = '[%(name)s] [%(levelname)s] : %(message)s'
    logging.basicConfig(format=formatter)
    # formatter = '[%(asctime)s] [%(levelname)s] [%(name)s] [%(message)s]'
    logger = logging.getLogger(__application__)
    logger.setLevel(logging.getLevelName(level.upper()))
    # logging.basicConfig(level=logging.getLevelName(level.upper()),
    #                     format=formatter)


def convert_type(value, value_type):
    """
    Convert a string value to the specific type

    :param value: value to convert
    :param value_type: destination type
    :return: the converted object
    """
    if value_type == 'string':
        return str(value)

    try:
        converted_object = ast.literal_eval(value)
    except SyntaxError:
        raise Exception('provided value is a malformed object')

    if value_type not in ['list', 'dict']:
        raise Exception('value type: {t} not supported'.format(t=value_type))

    try:
        if value_type == 'list':
            assert type(converted_object) == list
        elif value_type == 'dict':
            assert type(converted_object) == dict
    except AssertionError:
        raise Exception('Provided value does not match with the type: {t}'.format(t=value_type))
    return converted_object


def main():
    """
    Command line tool to use some functionality of the S3Vault

    :return:
    """
    args = check_args()
    configure_logging(args.log_level)
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    token_factory = TokenFactory()
    conn_manager = ConnectionFactory(region=args.region, profile_name=args.profile, token=token_factory.token)

    if args.command == 'template':
        try:
            # expose the environemnt variables in 2 dicts
            s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
            ansible_env = copy.deepcopy(os.environ)
            environment = copy.deepcopy(os.environ)
            args.dest.write(s3vault.render_template(args.template.name,
                                                    ansible_env=ansible_env,
                                                    environment=environment))
        except Exception as e:
            logger.exception('Error while expanding the template. Exiting')
            sys.exit(1)
    elif args.command == 'push':
        try:
            s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
            logger.info(args.src.name)
            metadata = s3vault.put_file(src=args.src.name,
                                        dest=args.dest,
                                        encryption_key_arn=args.kms_arn,
                                        key_alias=args.kms_alias)
            logger.debug('s3fsobject metadata: {d}'.format(d=metadata))
        except Exception as e:
            logger.exception('Error while pushing file. Error: {t} / {e}'.format(t=str(type(e)),
                                                                                 e=str(e)))
            sys.exit(1)
    elif args.command == 'configset':
        try:
            s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
            metadata = s3vault.set_property(configfile=args.config,
                                            key=args.key,
                                            value=convert_type(args.value, args.value_type),
                                            encryption_key_arn=args.kms_arn,
                                            key_alias=args.kms_alias)
            logger.debug('s3fsobject metadata: {d}'.format(d=metadata))
        except Exception as e:
            logger.exception('Error while setting property. Error: {t} / {e}'.format(t=str(type(e)),
                                                                                     e=str(e)))
    elif args.command == 'create_session':
        try:
            external_id = getpass('External ID:')
            token_factory = TokenFactory(role_name=args.role_name, external_id=external_id)
            token_factory.generate_token()
        except Exception as e:
            logger.exception('Error while setting the token. Type: {t}. Error: {e}'.format(t=str(type(e)), e=str(e)))
            sys.exit(1)
        if token_factory.token:
            logger.info('Token created successfully. Expiration: {e}'.format(e=str(token_factory.token['Expiration'])))
    elif args.command == 'create_s3vault_config':
        shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 's3vault.example.yml'),
                     args.output_file.name)
        logger.info('S3Vault configuration file created: {}'.format(args.output_file.name))
    elif args.command == 'create_cloudformation':
        try:
            s3vault_config = ConfigManager(args.s3vault_config.name).load_config()
            policy_manager = PolicyManager(s3vault_config)
            with open(args.output_file.name, 'wb') as cf_file:
                cf_file.write(policy_manager.generate_cloudformation())
        except Exception as e:
            logger.exception('Exception while generating CloudFormation.')
            sys.exit(1)
        logger.info('CloudFormation template generated: {}'.format(args.output_file.name))
    elif args.command == 'ansible_path':
        dirname = os.path.dirname(os.path.abspath(__file__))
        print('{}'.format(os.path.join(dirname, 'ansible')))
    else:
        logger.error('Command not available')
        sys.exit(1)


if __name__ == '__main__':
    main()

