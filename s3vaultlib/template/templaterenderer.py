#!/usr/bin/env python

import logging

import jinja2

from .. import __application__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class TemplateRenderer(object):
    """
    Renders a template based on S3Fs location
    """

    def __init__(self, template_file, s3fs):
        """

        :param template_file: template file to process
        :param s3fs: S3Fs object
        :type s3fs: S3Fs
        """
        self.logger = logging.getLogger('{a}.{m}'.format(a=__application__, m=self.__class__.__name__))
        self._template_file = template_file
        self._jinja2 = jinja2.Environment(trim_blocks=True, autoescape=False)
        # load additional ansible filters
        try:
            from ansible.plugins.filter.core import FilterModule
            self._jinja2.filters.update(FilterModule().filters())
        except ImportError:
            self.logger.info('Ansible not present, filter will not be added')
        self._s3fs = s3fs
        """ :type : S3Fs """

    def render(self, **kwargs):
        """
        Renders the template

        :param kwargs: additional variables to use in the rendering
        :return: content of the rendered template
        :rtype: basestring
        """
        with open(self._template_file, 'rb') as tpl_file:
            tpl_data = tpl_file.read().decode('utf-8')
        template = self._jinja2.from_string(tpl_data)
        variables = {obj.name: obj for obj in self._s3fs.objects}
        variables.update(kwargs)
        result = template.render(**variables)
        return result
