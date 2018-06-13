# -*- coding: utf-8 -*-
Feature: S3Vault uploading and encrypt a file

    Scenario Outline: Upload a file and validate the checksum
        Given we have the file named file_name
        Given we have a bucket named s3bucket
        Given we have a kms key with alias alias/kms_key
        Given we put the content <content> in the file_name
        When  we want upload file_name in bucket s3bucket at path s3path with name s3filename encrypted with key alias kms_key
        Then  the file must be present in bucket s3bucket at path s3path with name s3filename with checksum <checksum>

        Examples: File Contents
            | content      | checksum                         |
            | test_content | 27565f9a57c128674736aa644012ce67 |


    Scenario Outline: Upload a binary file
        Given we have a bucket named s3bucket
        Given we have a kms key with alias alias/kms_key
        Given we provision the fixture <fixture_name> in the workspace
        When  we want upload <fixture_name> in bucket s3bucket at path s3path with name s3filename encrypted with key alias kms_key
        Then  the file must be present in bucket s3bucket at path s3path with name s3filename with checksum <checksum>

        Examples: Binary Files
            | fixture_name | checksum                         |
            | testfile     | 011bd6f4ca93c98962bf581cef620846 |
            | testfile2    | 5fb6375a301f106e09e0528e592ed1bb |
