#!/usr/bin/env python
import logging
logging.basicConfig(level=logging.DEBUG)
from pprint import pprint

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"
from s3vaultlib.connectionfactory import ConnectionFactory
from s3vaultlib.policymanager import PolicyManager
from s3vaultlib.configmanager import ConfigManager

config = ConfigManager('/Users/giuseppechiesa/git/s3vaultlib/s3vaultlib/config.example.yml').load_config()
pol = PolicyManager(config)

with open('/tmp/peppe', 'w') as fp:
    fp.write(pol.with_connection_factory(ConnectionFactory(region='eu-west-1', profile_name='dev')).generate_cloudformation())

