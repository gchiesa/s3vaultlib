# -*- coding: utf-8 -*-
Feature: S3Vault getting a file

    Scenario Outline: Get a file and validate the checksum
        Given we have a bucket named s3bucket
        Given we have on s3bucket at path s3path the file s3filename with content <content>
        When  we get the file from s3bucket at path s3path with name s3filename
        Then  the checksum matches <checksum>

        Examples: File Contents
            | content      | checksum                         |
            | test_content | 27565f9a57c128674736aa644012ce67 |


    Scenario Outline:  Get a binary file
        Given we have a bucket named s3bucket
        Given we have on s3bucket at path s3path the file s3filename with fixture <fixture_name>
        When  we get the file from s3bucket at path s3path with name s3filename
        Then  the checksum matches <checksum>

        Examples:
            | fixture_name | checksum |
            | testfile     | 011bd6f4ca93c98962bf581cef620846 |
            | testfile2    | 5fb6375a301f106e09e0528e592ed1bb |

