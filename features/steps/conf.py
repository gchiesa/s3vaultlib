#!/usr/bin/env python
import logging
import os
import tempfile

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017-2021, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

WORKSPACE = tempfile.mkdtemp('bdd_')
FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', 'fixtures')
