S3Vaultlib
==========

|pypi| |build status| |code quality| |documentation| |3rd party libs|

S3Vaultlib is a Python Library and CLI tool that enable you to
implements a secure vault / configuration datastore for your AWS
platform by using AWS resources: CloudFormation, S3, IAM, KMS S3Vaultlib
it’s **yet another vault** with the goal to give easy maintainability,
use only AWS resource and with strong security patterns in mind.

Why a vault?
------------

It’s a common pattern in SRE and DevSecOps to create resources
environment unaware and configure the resource automatically when is
deployed in a specific environment

S3Vaultlib Features
-------------------

-  Use Server Side Encryption to store the objects on S3 with per-role
   KMS key

-  Use per role encryption with least privilege patterns to access the
   vault. Each role in the vault **can only consume** its own
   keymaterials

-  Special elevated privileged mode with a specific role able to produce
   and configure keymaterials, with only temporary access

-  Save, retrieve, update objects in the vault

-  Integrates flawlessly with Ansible by exposing an action plugin that
   allows you to expand templates by using variables / keymaterials from
   the vault

-  Powerful CLI to create, manage and update the objects in the vault

-  Easy maintainable via simple yaml file

-  Expose a flexyble python library to extend functionalities or
   implement the retrieval of keymaterials from your code.

S3vaultlib Architecture
-----------------------

**S3Vaultlib requires no installation or security patches / updates.**
The architecture leverages entirely on AWS existing resource to create a
secure vault with Role Base Access Control, versioning and region
awareness.

It integrates with the **IAM** to generate the necessary roles and
policies, **KMS** to generate per-role keys, **S3** to configure the
bucket policies to enforce high level of security and **CloudFormation**
to create the Infrastructure as Code that combine all the above in a
powerful vault.

Check In depth Architecture for more information

HOW-TOs
-------

Example scenarios
~~~~~~~~~~~~~~~~~

-  Provisioning a vault: A simple example to see how to provision a vault via the command line
   interface
-  Configure NGINX with S3Vaultlib: A simple
   example where we deploy an environment unaware NGINX instance and
   it’s configured via S3Vaultlib ansible plugin

CLI Usage
~~~~~~~~~

The complete documentation can be found here:
CLI Usage

Alternatives
------------

Currently there are several alternative patterns used.

-  | Configuration / Keymaterials encrypted in git
   | **Please don’t do this, really!**

-  | `Vault <https://www.vaultproject.io/>`__ by Hashicorp
   | Full featured vault system, widely used in the DevOPS community.
     But it’s also yet another system to deploy and maintain in high
     availability and also, it requires keymaterials for the
     installation (since is not a native AWS component)

-  | `AWS Secret Manager <https://aws.amazon.com/secrets-manager/>`__
   | Very valid alternative offered by AWS. Still lack a bit of
     flexibility to be used transparently in your bootstrap pipelines
     for EC2 / Dockers / Lambdas / Applications

.. |pypi| image:: https://img.shields.io/pypi/v/s3vaultlib.svg
   :target: https://pypi.python.org/pypi/s3vaultlib
.. |build status| image:: https://travis-ci.org/gchiesa/s3vaultlib.svg?branch=master
   :target: https://travis-ci.org/gchiesa/s3vaultlib
.. |code quality| image:: https://api.codacy.com/project/badge/Grade/902b192986194c1c9ec3f385e4db31c0
   :target: https://www.codacy.com/app/peppechiesa/s3vaultlib?utm_source=github.com&utm_medium=referral&utm_content=gchiesa/s3vaultlib&utm_campaign=Badge_Grade
.. |documentation| image:: https://readthedocs.org/projects/s3vaultlib/badge/?version=latest
   :target: https://s3vaultlib.readthedocs.io/en/latest/?badge=latest
.. |3rd party libs| image:: https://pyup.io/repos/github/gchiesa/s3vaultlib/shield.svg
   :target: https://pyup.io/repos/github/gchiesa/s3vaultlib/
