#!/usr/bin/env python

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def write_with_modecheck(file_handler, data):
    if file_handler.mode == 'w':
        file_handler.write(data.decode('utf-8'))
    else:
        file_handler.write(data)
