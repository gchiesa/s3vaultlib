#!/usr/bin/env python
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError, ScannerError
from io import StringIO

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def build_parser(*args, **kwargs):
    y = YAML(typ='safe')
    y.default_flow_style = kwargs.get('default_flow_style', False)
    y.explicit_start = kwargs.get('explicit_start', True)
    y.indent = kwargs.get('indent', 2)
    return y


def load_to_string(data):
    y = build_parser()
    return y.load(data)


def write_to_string(data):
    y = build_parser()
    dst = StringIO()
    y.dump(data, dst)
    return dst.getvalue()


def write_to_file(data, filename):
    with open(filename, 'wb') as fh:
        fh.write(write_to_string(data))


__all__ = [
    'build_parser',
    'load_to_string',
    'write_to_string',
    'write_to_file',
    'ParserError',
    'ScannerError'
]
