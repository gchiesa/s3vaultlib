import json
import os
import subprocess

from behave import *
from hamcrest import *

from conf import FIXTURES_PATH, WORKSPACE
from s3vaultlib.cloudformation.policymanager import PolicyManager


@step('we generate the cloudformation')
def step_impl(context):
    p = PolicyManager(context.config_manager)
    context.policy_manager = p
    context.cloudformation = p.generate_cloudformation()


@then("the generated data matches the target fixture {cloudformation}")
def step_impl(context, cloudformation):
    with open(os.path.join(FIXTURES_PATH, cloudformation), 'rb') as ch:
        d = ch.read()
    assert_that(json.loads(context.cloudformation), equal_to(json.loads(d)))


@step("the generated data is valid cloudformation data")
def step_impl(context):
    with open('{}'.format(os.path.join(WORKSPACE, 'template.out')), 'wb') as fh:
        fh.write(context.cloudformation.encode('utf-8'))
    retcode = subprocess.check_call([
        'cfn-lint',
        '--ignore-checks', 'W3005',
        '--ignore-checks', 'W3011',
        '--template', '{}'.format(os.path.join(WORKSPACE, 'template.out'))
    ])
    assert_that(retcode, equal_to(0))
