#!/usr/bin/env python
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError, ScannerError
from six import StringIO

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017-2021, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def build_parser(*args, **kwargs):
    y = YAML(typ=kwargs.get('loader', 'safe'))
    y.default_flow_style = kwargs.get('default_flow_style', False)
    y.explicit_start = kwargs.get('explicit_start', True)
    y.width = 4096
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def load_from_stream(stream):
    y = build_parser()
    return y.load(stream)


def write_to_string(data):
    y = build_parser(loader='rt')
    dst = StringIO()
    y.dump(data, dst)
    return dst.getvalue()


def write_to_file(data, filename):
    with open(filename, 'wb') as fh:
        fh.write(write_to_string(data).encode())


__all__ = [
    'build_parser',
    'load_from_stream',
    'write_to_string',
    'write_to_file',
    'ParserError',
    'ScannerError'
]
