#!/usr/bin/env python
import argparse
import logging.config
import sys

from . import __application__
from . import __version__
from .commands import *
from .connection.connectionfactory import ConnectionFactory
from .connection.tokenfactory import TokenFactory

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

    parser = argparse.ArgumentParser(prog='s3v', description='S3Vault Command Line Interface')
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
    parser.add_argument('--disable-ec2', '--no-ec2', '--local', dest='disable_ec2', required=False,
                        help='Identifies if the commands are issued in a ec2 instance or via external devices',
                        action='store_true',
                        default=False)

    # <bucket>/<path>/
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('remote', help='Remote coordinates on the Vault. '
                                              'In the form <bucket>/<path>/[<source|destination|config>]')
    # KMS part
    kms = common_parser.add_mutually_exclusive_group()
    kms.add_argument('-k', '--kms-alias', dest='kms_alias', required=False,
                     default='',
                     help='Key alias to use to decrypt data')
    kms.add_argument('--kms-arn', dest='kms_arn', required=False,
                     default='',
                     help='Key arn to use to decrypt data')

    subparsers = parser.add_subparsers(dest='command')

    # TEMPLATE
    # s3v tpl bucket/sub/path/ -t test.tpl -d test.out
    template = subparsers.add_parser('template', aliases=('tpl',),
                                     help='Expand a template file based on a S3Vault',
                                     parents=[common_parser])
    """ :type : argparse.ArgumentParser """

    template.add_argument('-t', '--template', dest='template', required=False,
                          help='Template to expand from s3vault path (default stdin)',
                          type=argparse.FileType('rb'), default='-')
    template.add_argument('-d', '--dest', dest='dest', required=False,
                          help='Destination file (default stdout)',
                          type=argparse.FileType('wb'), default='-')

    # s3v push bucket/sub/path/ -s object [-d object]
    pushfile = subparsers.add_parser('obj-push', aliases=('push',),
                                     help='Push an object in the Vault',
                                     parents=[common_parser])
    """ :type : argparse.ArgumentParser """

    pushfile.add_argument('-s', '--src', dest='src', required=False,
                          help='Source file to upload',
                          type=argparse.FileType('rb'))
    pushfile.add_argument('-d', '--dest', dest='dest', required=False,
                          help='Destination name (default same as source)')

    # s3v pull bucket/sub/path/ -s object [-d object]
    getfile = subparsers.add_parser('obj-pull', aliases=('pull',),
                                    help='Pull an object in the Vault',
                                    parents=[common_parser])
    """ :type : argparse.ArgumentParser """

    getfile.add_argument('-s', '--src', dest='src', required=True,
                         help='Source file to retrieve')
    getfile.add_argument('-d', '--dest', dest='dest', required=False,
                         help='Destination name',
                         type=argparse.FileType('wb'), default='-')

    # s3v conf-set bucket/sub/path/ -c conf_object -K test -V test_value
    setproperty = subparsers.add_parser('conf-set', aliases=('set',),
                                        help='Set a property in a configuration file in the Vault',
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

    # s3v conf-edit bucket/sub/path/ -c conf_object
    editproperty = subparsers.add_parser('conf-edit', aliases=('edit',),
                                         help='Edit a configuration in the Vault',
                                         parents=[common_parser])
    """ :type : argparse.ArgumentParser """

    editproperty.add_argument('-c', '--config', dest='config', required=True,
                              help='Configuration object to edit')
    editproperty.add_argument('-t', '--type', dest='type', required=False,
                              choices=['yaml', 'json'],
                              default='yaml',
                              help='Editor type to use (yaml, json)')

    # s3v session -r RoleAdmin
    create_session = subparsers.add_parser('session',
                                           help='Create a new session with assume role')
    """ :type : argparse.ArgumentParser """

    create_session.add_argument('--no-eid', '--no-external-id', dest='no_external_id', action='store_true',
                                default=False,
                                help='Disable External ID verification')
    cs_role = create_session.add_mutually_exclusive_group()
    cs_role.add_argument('-r', '--role-name', dest='role_name', required=False,
                         help='Role to assume')
    cs_role.add_argument('-ra', '--role-arn', dest='role_arn', required=False,
                         help='Role Arn to assume')

    # s3v init
    create_s3vault_config = subparsers.add_parser('init',
                                                  help='Create a new Vault configuration file')
    """ :type : argparse.ArgumentParser """

    create_s3vault_config.add_argument('-o', '--output', dest='output_file', required=True,
                                       type=argparse.FileType('wb'),
                                       help='Config file to create (default stdout)', default='-')

    # s3v cloudformation -c s3vault.yml -o s3vault.template
    cloudformation_generate = subparsers.add_parser('cloudformation',
                                                    help='Generate a CloudFormation template from a Vault '
                                                         'configuration')
    """ :type : argparse.ArgumentParser """

    cloudformation_generate.add_argument('-c', '--config', dest='s3vault_config', required=True,
                                         type=argparse.FileType('rb'),
                                         help='Vault configuration file')
    cloudformation_generate.add_argument('-o', '--output', dest='output_file', required=False,
                                         type=argparse.FileType('wb'),
                                         help='CloudFormation output file', default='-')
    # ansible path
    _ = subparsers.add_parser('ansible-path', aliases=('ansible_path',),
                              help='Resolve the ansible module path')  # type: argparse.ArgumentParser
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
                'format': '[%(levelname)-8s] [%(name)s]: %(message)s'
            },
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': '%(log_color)s[%(levelname)-8s]%(reset)s %(thin_white)s[%(name)s]%(reset)s : %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level.upper(),
                'formatter': 'colored',
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


def main():
    """
    Command line tool to use some functionality of the S3Vault

    :return:
    """
    args = check_args()
    configure_logging(args.log_level)
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    token_factory = TokenFactory(is_ec2=is_ec2(args))
    conn_manager = ConnectionFactory(region=args.region, profile_name=args.profile, token=token_factory.token,
                                     is_ec2=is_ec2(args))

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
            command_createtoken(args, conn_manager)
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
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.exception('{m}. Error: {t} / {e}'.format(m=exception_message, t=str(type(e)), e=str(e)))
        else:
            logger.error('{m}. Error: {t} / {e}'.format(m=exception_message, t=str(type(e)), e=str(e)))
        sys.exit(1)


if __name__ == '__main__':
    main()
