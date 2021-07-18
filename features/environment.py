# #!/usr/bin/env python
import os

from moto import mock_kms, mock_s3

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017-2021, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

MOCK_S3 = None
MOCK_KMS = None


def before_scenario(context, scenario):
    global MOCK_S3, MOCK_KMS
    MOCK_KMS = mock_kms()
    MOCK_KMS.start()
    MOCK_S3 = mock_s3()
    MOCK_S3.start()


def after_scenario(context, scenario):
    global MOCK_S3, MOCK_KMS
    MOCK_KMS.reset()
    MOCK_S3.reset()
