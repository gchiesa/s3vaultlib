import os
import shutil
from hamcrest import *
from behave import *

from s3vaultlib.configmanager import ConfigManager, ConfigException
from conf import FIXTURES_PATH, WORKSPACE


@given('we provision the fixture {file_name} in the workspace as {s3vaultconfig}')
def step_impl(context, file_name, s3vaultconfig):
    shutil.copy2(os.path.join(FIXTURES_PATH, file_name), '{}'.format(os.path.join(WORKSPACE, s3vaultconfig)))


@when('we parse the {s3vaultconfig}')
def step_impl(context, s3vaultconfig):
    c = ConfigManager('{}'.format(os.path.join(WORKSPACE, s3vaultconfig)))
    assert_that(c.load_config(), instance_of(ConfigManager))
    context.config_manager = c


@when('we check the exception while parsing {s3vaultconfig}')
def step_impl(context, s3vaultconfig):
    c = ConfigManager('{}'.format(os.path.join(WORKSPACE, s3vaultconfig)))
    try:
        c.load_config()
    except Exception as e:
        context.exception = e


@then('configmanager has the {role_name} with the {key_name} that matches with {key_value}')
def step_impl(context, role_name, key_name, key_value):
    r = next((r for r in context.config_manager.roles if r.name == role_name), None)
    assert_that(r, not_none())
    assert_that(str(getattr(r, key_name, None)), equal_to(key_value))


@then("an exception type: {exception_type} is raised with text: {match}")
def step_impl(context, exception_type, match):
    assert_that(context.exception, instance_of(ConfigException))
    assert_that(str(context.exception), contains_string(match))


@then('configmanager has the {role_name} with the {key_name} not containing {key_value}')
def step_impl(context, role_name, key_name, key_value):
    r = next((r for r in context.config_manager.roles if r.name == role_name), None)
    assert_that(r, not_none())
    assert_that(key_value, not_(is_in(getattr(r, key_name, None))))
