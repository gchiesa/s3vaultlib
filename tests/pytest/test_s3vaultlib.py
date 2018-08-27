# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """Tests for `s3vaultlib` package."""
# from io import BytesIO, FileIO
#
# import tests.pytest
# from moto import mock_s3, mock_ec2, mock_kms
# from s3vaultlib.connectionfactory import ConnectionFactory
# from s3vaultlib.s3vaultlib import S3Vault
# import boto3
# import os
#
# class s3config(object):
#     bucket = 'test_bucket'
#     path = '123/456/789/'
#     file_data = """example file\nmultiline\nutf-8\nκόσμε"""
#     file_name = 'test_file'
#
# @tests.pytest.fixture
# def response():
#     """Sample pytest fixture.
#
#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
#
#
# @tests.pytest.fixture(scope='module')
# @mock_s3
# def s3_setup():
#     s3 = boto3.client('s3')
#     """ :type : pyboto3.s3 """
#     bucket = s3.create_bucket(s3config.bucket)
#     with open('test_file', 'wb') as fh:
#         fh.write(s3config.file_data)
#     s3.upload_file('test_file', s3config.bucket, '{}'.format(os.path.join(s3config.path, s3config.file_name)))
#
#
# @tests.pytest.fixture(scope='module')
# @mock_s3
# @mock_ec2
# @mock_kms
# def s3vault_instance():
#     conn = ConnectionFactory(region='eu-west-1')
#     return S3Vault(s3config.bucket, s3config.path, conn)
#
#
# @mock_s3
# def test_s3vault_get_file(s3vault_instance):
#     """
#     :type s3vault_instance : S3Vault
#     :param s3vault_instance:
#     :return:
#     """
#     f = s3vault_instance.get_file(s3config.file_name)
#     assert f == s3config.file_data
