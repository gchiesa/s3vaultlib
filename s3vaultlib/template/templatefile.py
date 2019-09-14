#!/usr/bin/env python

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class TemplateFileException(Exception):
    pass


class TemplateFile(object):
    def __init__(self, filename):
        self._filename = filename
        self._template_data = None

    @property
    def filename(self):
        return self._filename

    def _get_template_content(self):
        with open(self._filename, 'rb') as fh:
            self._template_data = fh.read().decode('utf-8')

    @property
    def template_data(self):
        if not self._template_data:
            self._get_template_content()
        return self._template_data

    def _get_raw_copy_filename(self):
        data = self.template_data.strip()
        if data[0:2] != '{{' or data[-2:] != '}}':
            raise ValueError()
        inner_data = data[2:-2]
        if '|' in inner_data:
            raise ValueError()
        return inner_data.strip()

    def is_raw_copy(self, s3fs_objects):
        """
        Detect if the template represent a raw copy of the file

        :param template_file:
        :param s3fs_objects:
        :return:
        """
        try:
            filename = self._get_raw_copy_filename()
        except ValueError:
            return False
        if filename not in [obj.name for obj in s3fs_objects]:
            return False
        return True

    def get_raw_copy_src(self):
        try:
            filename = self._get_raw_copy_filename()
        except ValueError:
            return None
        return filename
