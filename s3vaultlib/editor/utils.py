#!/usr/bin/env python
from __future__ import unicode_literals

import json
import re

from ..utils import yaml
from ..utils.yaml import ParserError, ScannerError

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def extract_tokens(dict_data, result_list):
    if isinstance(dict_data, dict):
        for item in dict_data.values():
            extract_tokens(item, result_list)
        result_list.extend(dict_data.keys())
    elif isinstance(dict_data, list) or isinstance(dict_data, tuple):
        for item in dict_data:
            extract_tokens(item, result_list)


def json_fixer(json_data):
    result = '{}'
    try:
        result = json.loads(json_data)
        return result
    except ValueError as e:
        pass
    try:
        error_pos = int(re.findall(r'\(char (\d+)\)', str(e))[0])
    except IndexError:
        error_pos = len(json_data)
    # try to fix it
    valid_chunk, _, _ = json_data[:error_pos].strip().rpartition(':')
    fixers = [
        ('"', ':""}'),
        (',', "{}}"),
    ]
    for f in fixers:
        if valid_chunk.endswith(f[0]):
            result = '{v}{f}'.format(v=valid_chunk, f=f[1])
            break
    try:
        return json.loads(json_data)
    except ValueError:
        pass
    return json.loads(result)


def yaml_fixer(yaml_data):
    to_fix = yaml_data.strip()
    result = ''
    error_pos = 0
    try:
        result = yaml.load_to_string(to_fix)
        return result
    except (ParserError, ScannerError) as e:
        error_pos = e.problem_mark.index
    # search the last newline
    last_valid_position = to_fix[:error_pos].rfind('\n')
    valid_chunk = to_fix[:last_valid_position]
    try:
        return yaml.load_to_string(valid_chunk)
    except (ParserError, ScannerError):
        pass
    return yaml.load_to_string(result)
