#!/usr/bin/env python
from __future__ import unicode_literals

import cgi
import json
import logging
import sys

import six
import yaml
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.lexers.data import YamlLexer, JsonLexer
from pygments.styles import get_style_by_name
from yaml.loader import ParserError

from .completers import CompleteFromDocumentKeys
from .validators import YAMLValidator, JSONValidator
from .autosuggestions import AutosuggestFromDocumentData
from .. import __application__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

DEFAULT_STYLE = 'native'


class EditorException(Exception):
    pass


class EditorAbortException(Exception):
    pass


class Editor(object):
    SUPPORTED_MODE = ('json', 'yaml')
    VALIDATORS = {
        'yaml': YAMLValidator,
        'json': JSONValidator
    }
    LEXERS = {
        'yaml': YamlLexer,
        'json': JsonLexer
    }

    def __init__(self, json_data, attributes=None, mode='json'):
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._data = json_data
        self._mode = mode
        self._bindings = None
        self._completer = None
        self._attributes = attributes
        self._result = None
        if self._mode not in self.SUPPORTED_MODE:
            raise EditorException('Invalid editor mode. Supported mode: {}'.format(self.SUPPORTED_MODE))
        try:
            json.loads(self._data)
        except Exception as e:
            raise EditorException('Invalid data. Error: {t}. Message: {e}'.format(t=str(type(e)), e=str(e)))

    def _load_key_bindings(self):
        self._bindings = KeyBindings()

        @self._bindings.add('tab')
        def _(event):
            event.app.current_buffer.insert_text('  ')

        # @self._bindings.add('c-space')
        # def _(event):
        #     buff = event.app.current_buffer
        #     if buff.complete_state:
        #         buff.complete_next()
        #     else:
        #         buff.start_completion(select_first=False)
        # return self._bindings

    def bottom_bar(self):
        data = [
            '<b>{}</b>'.format(cgi.escape('<ESC> + <Enter> to save and exit')),
            '<b>{}</b>'.format(cgi.escape('<CTRL> + <C> exit without save'))
        ]
        if self._attributes.get('config', None):
            data += ['<b>Configuration</b>: {}'.format(cgi.escape(self._attributes['config']))]
        if self._attributes.get('bucket', None):
            data += ['<b>Bucket</b>: {}'.format(cgi.escape(self._attributes['bucket']))]
        if self._attributes.get('path', None):
            data += ['<b>Path</b>: {}'.format(cgi.escape(self._attributes['path']))]
        if self._attributes.get('debug', None):
            data += ['<b>Debug</b>: {}'.format(cgi.escape(self._attributes['debug']))]
        text = ' - '.join(data)
        return HTML(text.decode('utf-8'))

    @property
    def data(self):
        tmp = json.loads(self._data)
        if self._mode == 'yaml':
            return yaml.safe_dump(tmp,
                                  default_flow_style=False,
                                  explicit_start=True,
                                  indent=2)
        elif self._mode == 'json':
            return json.dumps(tmp, indent=4, separators=(',', ': '))
        else:
            raise EditorException('Invalid editor mode')

    @property
    def validator_class(self):
        return self.VALIDATORS.get(self._mode)

    @property
    def lexer_class(self):
        return self.LEXERS.get(self._mode)

    def _validate(self, result):
        try:
            if self._mode == 'yaml':
                return yaml.safe_load(result)
            elif self._mode == 'json':
                return json.loads(result)
        except ParserError:
            raise EditorException('Invalid YAML produced. Nothing will be saved')
        except ValueError:
            raise EditorException('Invalid JSON produced. Nothing will be saved')

    def run(self):
        self._load_key_bindings()
        style = style_from_pygments_cls(get_style_by_name(DEFAULT_STYLE))
        session = PromptSession(multiline=True,
                                lexer=PygmentsLexer(self.lexer_class),
                                validator=self.validator_class(),
                                bottom_toolbar=self.bottom_bar,
                                mouse_support=False,
                                style=style,
                                include_default_pygments_style=False,
                                validate_while_typing=True,
                                key_bindings=self._bindings,
                                completer=CompleteFromDocumentKeys(bottom_toolbar_attributes=self._attributes,
                                                                   mode=self._mode),
                                # auto_suggest=AutosuggestFromDocumentData(bottom_toolbar_attributes=self._attributes),
                                complete_while_typing=True,
                                )
        try:
            result = session.prompt('', default=six.text_type(self.data))
        except KeyboardInterrupt:
            self.logger.debug('Editing aborted.')
            raise EditorAbortException
        self._result = self._validate(result)

    @property
    def result(self):
        if self._result:
            return json.dumps(self._result)
        return ''


if __name__ == '__main__':
    # edit a file
    filename = sys.argv[1]
    with open(filename, 'rb') as fh:
        data = fh.read()

    editor = Editor(data, attributes={'debug': 'enabled'}, mode=sys.argv[2])
    editor.run()
    print('Result:\n---\n{}'.format(editor.result))
