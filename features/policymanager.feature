# Created by gchiesa at 05/07/2018
Feature: Policy Manager Coudformation Generator

    Scenario Outline: Cloudformation Generation from fixture config
        Given we provision the fixture <file_name> in the workspace as s3vaultconfig.yml
        When we parse the s3vaultconfig.yml
        And we generate the cloudformation
        Then the generated data matches the target fixture <cloudformation>
        And the generated data is valid cloudformation data

        Examples:
            | file_name          | cloudformation             |
            | s3vaultconfig1.yml | cf_s3vaultconfig1.template |
