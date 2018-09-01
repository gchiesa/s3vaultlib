#!/usr/bin/env python

import pytest

from s3vaultlib.editor.utils import extract_tokens, yaml_fixer

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def test_extract_tokens_contains_only_keys():
    fixture = {
        'level1key1': 'v_level1key1',
        'level1key2': {'level2key1': 'v_level2key1'},
        'level1key3': [
            'v_level2key3_0',
            'v_level2key3_1',
            'v_level2key3_2'
        ],
        'level1key4': {
            'level2key1': {
                'level3key1': 'v_level3key1'
            }
        }
    }
    tokens = []
    extract_tokens(fixture, tokens)
    tokens = set(sorted(tokens))
    values = [v for v in tokens if v.startswith('v_')]
    assert values == []


def test_extract_tokens_are_sorted():
    fixture = {
        'a': 'v_a',
        'b': {'c': 'v_c'},
        'd': [
            'v_d0',
            'v_d1',
            'v_d2'
        ],
        'e': {
            'f': {
                'g': 'v_g'
            }
        }
    }
    tokens = []
    extract_tokens(fixture, tokens)
    tokens = sorted(list(set(tokens)))
    assert tokens == ['a', 'b', 'c', 'd', 'e', 'f', 'g']


def test_extract_token_single_level_dict():
    fixture = {
        "username": "v_username",
        "password": "v_password",
        "hostname": "v_hostname"
    }
    tokens = []
    extract_tokens(fixture, tokens)
    tokens = sorted(list(set(tokens)))
    assert tokens == ['hostname', 'password', 'username']


@pytest.mark.parametrize('initial,fixed', [
    (
        '--- \nAction: \n- s3:Put* \nEffect: Allow \nResource: \n- arn:aws:s3:::my_bucket_example/webserver/* \n- arn:aws:s3:::my_bucket_example/mysql_instance/* \n:Sid\n',
        {'Action': ['s3:Put*'],
         'Resource': ['arn:aws:s3:::my_bucket_example/webserver/*', 'arn:aws:s3:::my_bucket_example/mysql_instance/*'],
         'Effect': 'Allow'}
    ),
    (
        '--- \nAction: \n- s3:Put* \nEffect: Allow \nResource: \n- arn:aws:s3:::my_bucket_example/webserver/* \n- arn:aws:s3:::my_bucket_example/mysql_instance/* \nSid\n',
        {'Action': ['s3:Put*'],
         'Resource': ['arn:aws:s3:::my_bucket_example/webserver/*', 'arn:aws:s3:::my_bucket_example/mysql_instance/*'],
         'Effect': 'Allow'}
    )
])
def test_yaml_fixer(initial, fixed):
    assert yaml_fixer(initial) == fixed
