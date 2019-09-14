#!/usr/bin/env python
import logging
import six
import abc
from boto3 import session

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@six.add_metaclass(abc.ABCMeta)
class MetadataBase:
    def __init__(self, session_info=None):
        self._session = session.Session(**session_info)

    @property
    @abc.abstractmethod
    def role(self):
        pass

    @property
    @abc.abstractmethod
    def account_id(self):
        pass

    @property
    @abc.abstractmethod
    def region(self):
        pass

    @property
    @abc.abstractmethod
    def instance_id(self):
        pass
