#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

from .utils import json_fixer, extract_tokens, yaml_fixer

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class AutosuggestFromDocumentData(AutoSuggest):
    def __init__(self, bottom_toolbar_attributes=None, mode='json', **kwargs):
        super(AutosuggestFromDocumentData, self).__init__()
        self._token_list = []
        self._mode = mode
        self._bottom_toolbar_attributes = bottom_toolbar_attributes

    def _tokenize(self, dict_data):
        self._token_list = []
        extract_tokens(dict_data, self._token_list)
        return sorted(list(set(self._token_list)))

    def get_suggestion(self, buffer, document):
        try:
            if self._mode == 'json':
                dict_data = json_fixer(buffer.text)
            else:
                dict_data = yaml_fixer(buffer.text)
        except Exception:
            dict_data = {}
        self._token_list = self._tokenize(dict_data)
        if self._bottom_toolbar_attributes.get('debug'):
            self._bottom_toolbar_attributes['debug'] = 'tokens: {}'.format(self._token_list)
        last_word = document.get_word_before_cursor().replace('"', '')
        if len(last_word) < 1:
            return
        for t in self._token_list:
            if t.startswith(last_word):
                return Suggestion(t[len(last_word):].decode('utf-8'))
