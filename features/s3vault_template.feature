# -*- coding: utf-8 -*-
Feature: S3Vault rendering templates

  Scenario Outline: Render a template with variables
    Given we have a bucket named s3bucket
    Given we have on s3bucket at path s3path the file s3conf with content <json_content>
    When  we render the template with content <tpl_content>
    Then  the checksum matches <checksum>

    Examples: File Contents
      | json_content                     | tpl_content                                  | result      | checksum                         |
      | {"a": true, "b": 1, "c": "test"} | {{ s3conf.a }},{{ s3conf.b }},{{ s3conf.c }} | True,1,test | e3d1a8b8a14081ecf96b9e7c495add21 |
      | {"a": {"b": {"c": [1,2]}}}       | {{ s3conf.a.b.c }}                           | [1, 2]      | 04cd0e0151f352e7fd414d694a604136 |


  Scenario Outline: Render a template with variables from file
    Given we have a bucket named s3bucket
    Given we have on s3bucket at path s3path the file s3filename with fixture <fixture_name>
    When  we render the template with content <tpl_content>
    Then  the checksum matches <checksum>

    Examples: File Contents
      | fixture_name   | tpl_content            | result | checksum                         |
      | testfile1.json | {{ s3filename.a.b.c }} | κόσμε  | 5fb6375a301f106e09e0528e592ed1bb |

