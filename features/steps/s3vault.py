#!/usr/bin/env python
import hashlib
import os
import shutil
from io import BytesIO
import json

import boto3
from behave import given, when, then

from conf import WORKSPACE, FIXTURES_PATH
from s3vaultlib.connectionfactory import ConnectionFactory
from s3vaultlib.s3vaultlib import S3Vault

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@given('we have the file named {file_name}')
def step_impl(context, file_name):
    """
    :type context: behave.runner.Context
    """
    with open('{}'.format(os.path.join(WORKSPACE, file_name)), 'wb') as fh:
        fh.write('test_data'.encode('utf-8'))


@when('we want upload {file_name} in bucket {s3bucket} at path {s3path} with name {s3filename} '
      'encrypted with key alias {kms_key}')
def step_impl(context, file_name, s3bucket, s3path, s3filename, kms_key):
    conn = ConnectionFactory('eu-west-1')
    s3v = S3Vault(s3bucket, s3path, conn)
    s3v.put_file(os.path.join(WORKSPACE, file_name), s3filename, key_alias=kms_key)


@given('we have a kms key with alias alias/{kms_key_alias}')
def step_impl(context, kms_key_alias):
    """
    :type context: behave.runner.Context
    """
    c = boto3.client('kms', region_name='eu-west-1')
    """ :type : pyboto3.kms """
    response = c.create_key(Description="mock", KeyUsage="ENCRYPT_DECRYPT", Origin="AWS_KMS")
    c.create_alias(AliasName='alias/{}'.format(kms_key_alias), TargetKeyId=response['KeyMetadata']['Arn'])


@given("we have a bucket named {s3bucket}")
def step_impl(context, s3bucket):
    """
    :type context: behave.runner.Context
    """
    c = boto3.client('s3')
    """ :type : pyboto3.s3 """
    c.create_bucket(Bucket=s3bucket)


@given("we put the content {content} in the {file_name}")
def step_impl(context, content, file_name):
    """
    :type context: behave.runner.Context
    :type content: str
    """
    with open('{}'.format(os.path.join(WORKSPACE, file_name)), 'wb') as fh:
        fh.write(content.encode('utf-8'))


@then("the file must be present in bucket {s3bucket} at path {s3path} with name {s3filename} with checksum {checksum}")
def step_impl(context, s3bucket, s3path, s3filename, checksum):
    """
    :type context: behave.runner.Context
    :type checksum: str
    """
    c = boto3.client('s3')
    """ :type : pyboto3.s3 """
    o = c.head_object(Bucket=s3bucket, Key=os.path.join(s3path, s3filename))
    assert o['ETag'] == '"{}"'.format(checksum)


@given("we have on {s3bucket} at path {s3path} the file {s3filename} with content {content}")
def step_impl(context, s3bucket, s3path, s3filename, content):
    c = boto3.client('s3')
    """ :type : pyboto3.s3 """
    print(type(content))
    c.put_object(Bucket=s3bucket, Key=os.path.join(s3path, s3filename), Body=BytesIO(content.encode('utf-8')))
    context.s3bucket = s3bucket
    context.s3path = s3path
    context.s3filename = s3filename


@when("we get the file from {s3bucket} at path {s3path} with name {s3filename}")
def step_impl(context, s3bucket, s3path, s3filename):
    conn = ConnectionFactory('eu-west-1')
    s3v = S3Vault(s3bucket, s3path, conn)
    d = s3v.get_file(s3filename)
    checksum = hashlib.md5()
    checksum.update(d)
    context.checksum = checksum.hexdigest()


@then("the checksum matches {checksum}")
def step_impl(context, checksum):
    assert context.checksum == checksum


@given("we provision the fixture {name} in the workspace")
def step_impl(context, name):
    shutil.copy2(os.path.join(FIXTURES_PATH, name), '{}'.format(os.path.join(WORKSPACE, name)))


@given("we have on {s3bucket} at path {s3path} the file {s3filename} with fixture {fixture_name}")
def step_impl(context, s3bucket, s3path, s3filename, fixture_name):
    c = boto3.client('s3')
    """ :type : pyboto3.s3 """
    with open(os.path.join(FIXTURES_PATH, fixture_name), 'rb') as fh:
        c.put_object(Bucket=s3bucket, Key=os.path.join(s3path, s3filename), Body=fh)
    context.s3bucket = s3bucket
    context.s3path = s3path
    context.s3filename = s3filename


@when("we render the template with content {tpl_content}")
def step_impl(context, tpl_content):
    conn = ConnectionFactory('eu-west-1')
    s3v = S3Vault(context.s3bucket, context.s3path, conn)
    tplname = '{}'.format(os.path.join(WORKSPACE, 'tpl'))
    with open(tplname, 'wb') as tplf:
        tplf.write(tpl_content.encode('utf-8'))
    outcome = s3v.render_template(tplname)
    print(outcome)
    checksum = hashlib.md5()
    checksum.update(outcome.encode('utf-8'))
    context.checksum = checksum.hexdigest()
