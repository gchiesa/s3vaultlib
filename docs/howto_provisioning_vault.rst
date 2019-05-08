.. _howto_provisioning_vault:

Provisioning a vault
====================

This document describe how to provision a vault using the S3Vaultlib CLI
and AWS CloudFormation (via the console)

Provisioning the S3Vault
------------------------

Let’s generate the default config with:

.. code:: bash

   s3vaultcli create_s3vault_config -o myconfig.yml

-  edit the example configuration by setting the target S3 bucket to use
   as vault. The output should look like the following (comments are
   stripped out):

.. code:: yaml

   ---
   s3vaultlib:
     vault:
       bucket: "test-bucket-for-s3-vault"
     roles:
       - name: role_admin
         privileges: [read, write]
         path: _all_
         managed_policies: []
       - name: role_webserver
         privileges: [read]
         kms_alias: role_webserver
         path:
           - webserver/
       - name: role_mysql
         privileges: [read]
         kms_alias: role_mysql
         path:
         - mysql/

-  with the CLI now we are going to create the cloudformation template
   for the vault

.. code:: bash

   s3vaultcli create_cloudformation -c test.yml -o test.template

-  Now in the AWS Console we enter CloudFormation and we create a new
   template from file and we upload ``test.template``. In a while we
   should have our vault completely configured.
