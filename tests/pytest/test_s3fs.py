#!/usr/bin/env python
import os

import pytest

from s3vaultlib.s3fs import S3Fs
from s3vaultlib.s3fs import S3FsObject
from s3vaultlib.s3fs import S3FsObjectException
from .fixtures import s3 as s3fixtures
from .mock.s3 import S3Mock
import six

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@pytest.mark.parametrize('key, expected', [
    ({'Key': '/'}, False),
    ({'Key': '/test1/test2'}, True),
    ({'Key': '/test1/'}, False),
    ({'Key': '/test1'}, True),
    ({'Key': 'test1'}, True)
])
def test_s3fs_is_file(key, expected):
    assert S3Fs.is_file(key) == expected


def test_s3fsobject_without_key():
    with pytest.raises(S3FsObjectException) as excinfo:
        _ = S3FsObject({}, None, None, None)
    assert 'Not a valid object' in str(excinfo.value)


@pytest.mark.parametrize('data, expect', [
    (v['list_objects_v2'], k) for k, v in six.iteritems(s3fixtures.S3_OBJECTS)
])
def test_s3fsobject_name(data, expect):
    assert S3FsObject(data, None, None, None).name == expect


def test_s3fsobject_loadcontent():
    obj = S3FsObject(s3fixtures.S3_OBJECTS['test_name']['list_objects_v2'], 'bucket', 'path', S3Mock())
    assert obj._load_content() == S3Mock().expect_body()


@pytest.mark.parametrize('path,expect', [
    ('level1key1', 'v_level1key1'),
    ('level1key2.level2key1', 'v_level2key1'),
    ('level1key3', ['v_level2key3_0', 'v_level2key3_1', 'v_level2key3_2']),
    ('level1key4.level2key1.level3key1', 'v_level3key1')
])
def test_s3fsobject_get_value(path, expect):
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
    assert S3FsObject._get_value(fixture, path) == expect


def test_s3fsobject_get_value_return_exception():
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
    with pytest.raises(KeyError) as excinfo:
        S3FsObject._get_value(fixture, 'level1key3.v_level2key3_0')
    assert 'is a leaf value, not a dict' in str(excinfo.value)


def test_s3fsobject_set_value_override_element():
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
    from copy import deepcopy
    d = deepcopy(fixture)
    d['level1key4']['level2key1']['level3key1'] = ['test1', 'test2', 'test3']
    obj = S3FsObject(s3fixtures.S3_OBJECTS['test_name']['list_objects_v2'], 'bucket', 'path', S3Mock())
    assert d == obj._set_value(fixture, 'level1key4.level2key1.level3key1', ['test1', 'test2', 'test3'])


def test_s3fsobject_set_value_add_element():
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
    from copy import deepcopy
    d = deepcopy(fixture)
    d['level1key4']['level2key2'] = {'level3key2': 'v_level3key2'}
    obj = S3FsObject(s3fixtures.S3_OBJECTS['test_name']['list_objects_v2'], 'bucket', 'path', S3Mock())
    assert d == obj._set_value(fixture, 'level1key4.level2key2', {'level3key2': 'v_level3key2'})
