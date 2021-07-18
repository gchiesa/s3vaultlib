#!/usr/bin/env python
from __future__ import unicode_literals

import json
import re

from prompt_toolkit.validation import Validator, ValidationError

from ..utils import yaml
from ..utils.yaml import ParserError, ScannerError
import six

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017-2021, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class JSONValidator(Validator):
    @staticmethod
    def validate(document):
        try:
            json.loads(document.text)
        except ValueError as e:
            matches = re.compile('.*\(char\s(\d+).*').findall(str(e))
            position = int(matches[0]) if matches else 0
            raise ValidationError(message=six.text_type(str(e)), cursor_position=int(position))
        except Exception:
            raise


class YAMLValidator(Validator):
    def validate(self, document):
        try:
            yaml.load_from_stream(document.text)
        except (ParserError, ScannerError) as e:
            raise ValidationError(message=six.text_type(str(e.problem)), cursor_position=e.problem_mark.index)
        except Exception:
            raise
