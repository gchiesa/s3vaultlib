#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.completion import Completer, Completion

from .utils import json_fixer, yaml_fixer, extract_tokens

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class CompleteFromDocumentKeys(Completer):
    def __init__(self, bottom_toolbar_attributes=None, mode='json', **kwargs):
        super(CompleteFromDocumentKeys, self).__init__(**kwargs)
        self._bottom_toolbar_attributes = bottom_toolbar_attributes
        self._mode = mode
        self._token_list = []

    def _tokenize(self, dict_data):
        self._token_list = []
        extract_tokens(dict_data, self._token_list)
        return sorted(list(set(self._token_list)))

    def get_completions(self, document, complete_event):
        try:
            if self._mode == 'json':
                dict_data = json_fixer(document.text)
            else:
                dict_data = yaml_fixer(document.text)
        except Exception:
            dict_data = {}
        self._token_list = self._tokenize(dict_data)
        last_word = document.get_word_before_cursor().replace('"', '')
        # debugging
        if self._bottom_toolbar_attributes.get('debug'):
            self._bottom_toolbar_attributes['debug'] = 'lw: {lw}, tokens: {t}'.format(lw=last_word, t=self._token_list)
        # matching
        if len(last_word) < 1:
            return
        for t in self._token_list:
            if t.startswith(last_word):
                yield Completion(t.decode('utf-8'), -len(last_word))
