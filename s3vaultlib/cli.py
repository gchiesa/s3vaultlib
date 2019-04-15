#!/usr/bin/env python
import argparse
import ast
import copy
import json
import logging
import logging.config
import os
import shutil
import sys
from getpass import getpass
from io import BytesIO

from . import __application__
from . import __version__
from .configmanager import ConfigManager
from .connectionfactory import ConnectionFactory
from .editor import Editor, EditorAbortException
from .policymanager import PolicyManager
from .s3vaultlib import S3Vault
from .tokenfactory import TokenFactory
from .utils import yaml

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

    parser = argparse.ArgumentParser(prog='s3vaultcli', description='s3vaultcli')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
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
    # template
    template = subparsers.add_parser('template', help='Expand a template file based on a S3Vault',
                                     parents=[common_parser])
    """ :type : argparse.ArgumentParser """
    template.add_argument('-t', '--template', dest='template', required=True,
                          help='Template to expand from s3vault path',
                          type=argparse.FileType('rb'))
    template.add_argument('-d', '--dest', dest='dest', required=True,
                          help='Destination file',
                          type=argparse.FileType('wb'))

    # push file
    pushfile = subparsers.add_parser('push', help='Push a file in the S3Vault',
                                     parents=[common_parser])
    """ :type : argparse.ArgumentParser """
    pushfile.add_argument('-s', '--src', dest='src', required=True,
                          help='Source file to upload',
                          type=argparse.FileType('rb'))
    pushfile.add_argument('-d', '--dest', dest='dest', required=True,
                          help='Destination name')

    # get file
    getfile = subparsers.add_parser('get', help='Get a file in the S3Vault',
                                    parents=[common_parser])
    """ :type : argparse.ArgumentParser """
    getfile.add_argument('-s', '--src', dest='src', required=True,
                         help='Source file to retrieve')
    getfile.add_argument('-d', '--dest', dest='dest', required=True,
                         help='Destination name',
                         type=argparse.FileType('wb'))

    # set property
    setproperty = subparsers.add_parser('configset', help='Set a property in a configuration file in the S3Vault',
                                        parents=[common_parser])
    """ :type : argparse.ArgumentParser """
    setproperty.add_argument('-c', '--config', dest='config', required=True,
                             help='Configuration file to manage')
    setproperty.add_argument('-K', '--key', dest='key', required=True,
                             help='Key to set')
    setproperty.add_argument('-V', '--value', dest='value', required=True,
                             help='Value to set')
    setproperty.add_argument('-T', '--type', dest='value_type', required=False,
                             choices=['int', 'string', 'list', 'dict', 'yaml', 'json'],
                             default='string',
                             help='Data type for the value')
    # edit property
    editproperty = subparsers.add_parser('configedit', help='Edit a configuration file in the S3Vault',
                                         parents=[common_parser])
    """ :type : argparse.ArgumentParser """
    editproperty.add_argument('-c', '--config', dest='config', required=True,
                              help='Configuration file to manage')
    editproperty.add_argument('-t', '--type', dest='type', required=False,
                              choices=['yaml', 'json'],
                              default='yaml',
                              help='Editor type to use (yaml, json)')
    # create session
    create_session = subparsers.add_parser('create_session', help='Create a new session with assume role')
    """ :type : argparse.ArgumentParser """
    create_session.add_argument('--no-eid', '--no-external-id', dest='no_external_id', action='store_true',
                                default=False,
                                help='Disable External ID verification')
    cs_role = create_session.add_mutually_exclusive_group()
    cs_role.add_argument('-r', '--role-name', dest='role_name', required=False,
                         help='Role to assume')
    cs_role.add_argument('-ra', '--role-arn', dest='role_arn', required=False,
                         help='Role Arn to assume')

    # create s3vaultconfig
    create_s3vault_config = subparsers.add_parser('create_s3vault_config',
                                                  help='Create a new s3vault configuration file')
    """ :type : argparse.ArgumentParser """
    create_s3vault_config.add_argument('-o', '--output', dest='output_file', required=True,
                                       type=argparse.FileType('wb'),
                                       help='Config file to create')
    # cloudformation generate
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
    # ansible path
    _ = subparsers.add_parser('ansible_path', help='Resolve the ansible module path')  # type: argparse.ArgumentParser
    return parser.parse_args()


def configure_logging(level):
    """
    Configure the logging level of the tool

    :param level: level to set
    :return:
    """
    dconfig = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '[%(name)s] [%(levelname)s] : %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level.upper(),
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            __application__: {
                'level': level.upper(),
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': level.upper(),
            'handlers': ['console']
        }
    }
    logging.config.dictConfig(dconfig)


def load_from_yaml(filename):
    if not os.path.expanduser(filename) or not os.access(filename, os.R_OK):
        raise Exception('Unable to read file: {}'.format(filename))
    with open(filename, 'r') as fh:
        data = yaml.load_to_string(fh)
    return data


def load_from_json(filename):
    if not os.path.expanduser(filename) or not os.access(filename, os.R_OK):
        raise Exception('Unable to read file: {}'.format(filename))
    with open(filename, 'r') as fh:
        data = json.load(fh)
    return data


def convert_type(value, value_type):
    """
    Convert a string value to the specific type

    :param value: value to convert
    :param value_type: destination type
    :return: the converted object
    """
    if value_type == 'string':
        return str(value)

    if value_type == 'int':
        return int(value)

    if value_type == 'yaml':
        return load_from_yaml(value)

    if value_type == 'json':
        return load_from_json(value)

    try:
        converted_object = ast.literal_eval(value)
    except SyntaxError:
        raise Exception('provided value is a malformed object')

    if value_type not in ['list', 'dict']:
        raise Exception('value type: {t} not supported'.format(t=value_type))

    try:
        if value_type == 'list' and not isinstance(converted_object, list):
            raise AssertionError()
        elif value_type == 'dict' and not isinstance(converted_object, dict):
            raise AssertionError()
    except AssertionError:
        raise Exception('Provided value does not match with the type: {t}'.format(t=value_type))
    return converted_object


def command_template(args, conn_manager):
    s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
    ansible_env = copy.deepcopy(os.environ)
    environment = copy.deepcopy(os.environ)
    args.dest.write(s3vault.render_template(args.template.name,
                                            ansible_env=ansible_env,
                                            environment=environment))


def command_push(args, conn_manager):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
    logger.info('Uploading file {s}'.format(s=args.src.name))
    metadata = s3vault.put_file(src=args.src,
                                dest=args.dest,
                                encryption_key_arn=args.kms_arn,
                                key_alias=args.kms_alias)
    logger.debug('Metadata: {d}'.format(d=metadata))


def command_get(args, conn_manager):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
    logger.info('Retrieving file {s}'.format(s=args.src))
    logger.debug('Metadata: {m}'.format(m=s3vault.get_file_metadata(args.src)))
    args.dest.write(s3vault.get_file(args.src))
    logger.debug('File successfully created: {d}'.format(d=args.dest.name))


def command_configset(args, conn_manager):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
    metadata = s3vault.set_property(configfile=args.config,
                                    key=args.key,
                                    value=convert_type(args.value, args.value_type),
                                    encryption_key_arn=args.kms_arn,
                                    key_alias=args.kms_alias)
    logger.debug('Metadata: {d}'.format(d=metadata))


def command_configedit(args, conn_manager):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    s3vault = S3Vault(args.bucket, args.path, connection_factory=conn_manager)
    logger.info('Editing config: {s}'.format(s=args.config))
    metadata = s3vault.get_file_metadata(args.config)
    json_data = s3vault.get_file(args.config)
    try:
        json.loads(json_data)
    except ValueError:
        logger.error('ConfigEdit can only edit json config data')
        raise
    attributes = {
        'bucket': args.bucket,
        'path': args.path,
        'config': args.config
    }
    editor = Editor(json_data.encode('utf-8'), attributes=attributes, mode=args.type)
    try:
        editor.run()
    except EditorAbortException:
        logger.warning('Config left unmodified.')
        return
    # process the result
    memoryfile = BytesIO(editor.result)
    metadata = s3vault.put_file(src=memoryfile,
                                dest=args.config,
                                encryption_key_arn=metadata.get('SSEKMSKeyId', ''))
    logger.info('Config: {c} updated successfully.'.format(c=args.config))
    logger.debug('Metadata: {m}'.format(m=metadata))


def command_createtoken(args):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    external_id = None
    if not args.no_external_id:
        # prompt external id for verification
        external_id = getpass('External ID:')
    token_factory = TokenFactory(role_name=args.role_name, role_arn=args.role_arn, external_id=external_id)
    token_factory.generate_token()
    if token_factory.token:
        logger.info('Token created successfully. Expiration: {e}'.format(e=str(token_factory.token['Expiration'])))


def command_createconfig(args):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_resources', 's3vault.example.yml'),
                 args.output_file.name)
    logger.info('S3Vault configuration file created: {}'.format(args.output_file.name))


def command_createcloudformation(args):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    s3vault_config = ConfigManager(args.s3vault_config.name).load_config()
    policy_manager = PolicyManager(s3vault_config)
    with open(args.output_file.name, 'wb') as cf_file:
        cf_file.write(policy_manager.generate_cloudformation().encode('utf-8'))
    logger.info('CloudFormation template generated: {}'.format(args.output_file.name))


def command_ansiblepath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    print('{}'.format(os.path.join(dirname, '_resources', 'ansible')))


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

    exception_message = 'Unknown exception.'
    try:
        if args.command == 'template':
            exception_message = 'Error while expanding the template.'
            command_template(args, conn_manager)
        elif args.command == 'push':
            exception_message = 'Error while pushing file.'
            command_push(args, conn_manager)
        elif args.command == 'get':
            exception_message = 'Error while getting file.'
            command_get(args, conn_manager)
        elif args.command == 'configset':
            exception_message = 'Error while setting property.'
            command_configset(args, conn_manager)
        elif args.command == 'configedit':
            exception_message = 'Error while editing configuration.'
            command_configedit(args, conn_manager)
        elif args.command == 'create_session':
            exception_message = 'Error while setting the token.'
            command_createtoken(args)
        elif args.command == 'create_s3vault_config':
            exception_message = 'Error while creating s3vault config example.'
            command_createconfig(args)
        elif args.command == 'create_cloudformation':
            exception_message = 'Exception while generating CloudFormation.'
            command_createcloudformation(args)
        elif args.command == 'ansible_path':
            exception_message = 'Error while retrieving ansible path'
            command_ansiblepath()
    except Exception as e:
        logger.exception('{m}. Error: {t} / {e}'.format(m=exception_message, t=str(type(e)), e=str(e)))
        sys.exit(1)


if __name__ == '__main__':
    main()
