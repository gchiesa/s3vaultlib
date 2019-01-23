#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import logging
import pytest

from s3vaultlib.editor.utils import extract_tokens, yaml_fixer
from s3vaultlib.utils.yaml import write_to_string

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@pytest.mark.parametrize('data,result', [
    (
        'test123',
        u'--- test123\n...\n'
    ),
    (
        {'key1': 1, 'key2': 2, 'key3': 3, 'key4': [41, 42, '43']},
        '''---
key1: 1
key2: 2
key3: 3
key4:
- 41
- 42
- '43'
'''
    ),
    #     (
    #         {'test1': {'test11': 'value κόσμε'}},
    #         '''
    # test1:
    #   test11: value κόσμε
    #         '''
    #     )
])
def test_write_to_string(data, result):
    assert write_to_string(data).strip() == result.strip()
