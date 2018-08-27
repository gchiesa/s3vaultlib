# Created by gchiesa at 05/07/2018
Feature: Configuration Manager Parser

    Scenario Outline: Parsing Role : Happy Flow
        Given we provision the fixture <file_name> in the workspace as s3vaultconfig.yml
        When we parse the s3vaultconfig.yml
        Then configmanager has the <role_name> with the <key_name> that matches with <key_value>

        Examples:
            | file_name          | role_name      | key_name         | key_value                       |
            | s3vaultconfig1.yml | webserver      | kms_alias        | webserver                       |
            | s3vaultconfig1.yml | webserver      | path             | ['webserver']                   |
            | s3vaultconfig1.yml | admin_role     | kms_alias        | admin_role                      |
            | s3vaultconfig1.yml | admin_role     | privileges       | ['read', 'write']               |
            | s3vaultconfig1.yml | admin_role     | path             | ['webserver', 'mysql_instance'] |
            | s3vaultconfig1.yml | admin_role     | managed_policies | ['managed_policy1']             |

    Scenario: Parsing a configfile with empty vault section
        Given we provision the fixture s3vaultconfig2.yml in the workspace as s3vaultconfig.yml
        When we check the exception while parsing s3vaultconfig.yml
        Then an exception type: ConfigManagerException is raised with text: Vault section empty

    Scenario: Parsing a configfile with missing bucket
        Given we provision the fixture s3vaultconfig2a.yml in the workspace as s3vaultconfig.yml
        When we check the exception while parsing s3vaultconfig.yml
        Then an exception type: ConfigManagerException is raised with text: No bucket configured for vault

    Scenario: Parsing a configfile with missing role name
        Given we provision the fixture s3vaultconfig3.yml in the workspace as s3vaultconfig.yml
        When we check the exception while parsing s3vaultconfig.yml
        Then an exception type: ConfigManagerException is raised with text: No role name provided for config

    Scenario: Parsing a configfile with no roles
        Given we provision the fixture s3vaultconfig4.yml in the workspace as s3vaultconfig.yml
        When we check the exception while parsing s3vaultconfig.yml
        Then an exception type: ConfigManagerException is raised with text: No roles configured

