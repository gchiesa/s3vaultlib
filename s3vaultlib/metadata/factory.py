#!/usr/bin/env python

from . import ec2, local

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class MetadataFactory(object):
    @staticmethod
    def get_instance(is_ec2=False, session_info=None):
        if is_ec2:
            return ec2.EC2Metadata(session_info=session_info)
        return local.LocalMetadata(session_info=session_info)
