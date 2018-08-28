#!/usr/bin/env python

from s3vaultlib.editor import Editor

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
    Editor.extract_tokens(fixture, tokens)
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
    Editor.extract_tokens(fixture, tokens)
    tokens = sorted(list(set(tokens)))
    assert tokens == ['a', 'b', 'c', 'd', 'e', 'f', 'g']
