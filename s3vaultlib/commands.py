#!/usr/bin/env python
import ast
import copy
import json
import logging
import logging.config
import os
import shutil
from getpass import getpass
from io import BytesIO

from . import __application__
from .cloudformation.policymanager import PolicyManager
from .config.configmanager import ConfigManager
from .connection.tokenfactory import TokenFactory
from .editor.editor import Editor, EditorAbortException
from .s3vaultlib import S3Vault, S3VaultObjectNotFoundException, S3VaultException
from .utils import yaml, io

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

__all__ = [
    "is_ec2",
    "command_ansiblepath",
    "command_configedit",
    "command_configset",
    "command_createcloudformation",
    "command_createconfig",
    "command_createtoken",
    "command_get",
    "command_push",
    "command_template",
]


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
    data = s3vault.render_template(args.template.name, ansible_env=ansible_env, environment=environment)
    io.write_with_modecheck(args.dest, data.encode())


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
    io.write_with_modecheck(args.dest, s3vault.get_file(args.src))
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
    remote_exists = False
    try:
        metadata = s3vault.get_file_metadata(args.config)
        json_data = s3vault.get_file(args.config)
        remote_exists = True
    except S3VaultObjectNotFoundException:
        logger.debug('Remote config does not exists. Initializing a new one...')
        metadata = {}
        json_data = '{ "example": "editme" }'

    if not remote_exists and not args.kms_arn and not args.kms_alias:
        raise S3VaultException('KMS parameters required when remote config does not exists')

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
    editor = Editor(json_data, attributes=attributes, mode=args.type)
    try:
        editor.run()
    except EditorAbortException:
        logger.warning('Config left unmodified.')
        return
    # process the result
    memoryfile = BytesIO(editor.result.encode())
    metadata = s3vault.put_file(src=memoryfile,
                                dest=args.config,
                                key_alias=args.kms_alias,
                                encryption_key_arn=metadata.get('SSEKMSKeyId', ''))
    logger.info('Config: {c} updated successfully.'.format(c=args.config))
    logger.debug('Metadata: {m}'.format(m=metadata))


def command_createtoken(args, conn_manager):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    external_id = None
    if not args.no_external_id:
        # prompt external id for verification
        external_id = getpass('External ID:')
    token_factory = TokenFactory(role_name=args.role_name, role_arn=args.role_arn, external_id=external_id,
                                 connection_factory=conn_manager)
    token_factory.generate_token()
    if token_factory.token:
        logger.info('Token created successfully. Expiration: {e}'.format(e=str(token_factory.token['Expiration'])))


def command_createconfig(args):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_resources', 's3vault.example.yml'), 'r') as fh:
        data = fh.read()
    io.write_with_modecheck(args.output_file, data)
    logger.info('S3Vault configuration file created: {}'.format(args.output_file.name))


def command_createcloudformation(args):
    logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=__name__))
    s3vault_config = ConfigManager(args.s3vault_config.name).load_config()
    policy_manager = PolicyManager(s3vault_config)
    io.write_with_modecheck(args.output_file, policy_manager.generate_cloudformation().encode('utf-8'))
    logger.info('CloudFormation template generated: {}'.format(args.output_file.name))


def command_ansiblepath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    print('{}'.format(os.path.join(dirname, '_resources', 'ansible')))


def is_ec2(args):
    if args.disable_ec2:
        return False
    return True
