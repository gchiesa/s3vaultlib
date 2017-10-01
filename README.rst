===============
S3Vault Library
===============


.. image:: https://img.shields.io/pypi/v/s3vaultlib.svg
        :target: https://pypi.python.org/pypi/s3vaultlib

.. image:: https://api.travis-ci.org/gchiesa/s3vaultlib.svg
        :target: https://travis-ci.org/gchiesa/s3vaultlib

.. image:: https://readthedocs.org/projects/s3vaultlib/badge/?version=latest
        :target: https://s3vaultlib.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/gchiesa/s3vaultlib/shield.svg
     :target: https://pyup.io/repos/github/gchiesa/s3vaultlib/
     :alt: Updates


Python library to expose S3 as vault to store encrypted data

Goal
----
When you need to deploy some server you always want to have a vault where to store the keymaterials used by the server.

Usually this means you need to deploy a sort of vault server to manage access control and encryption (like Vault from
Hashicorp). But also this service need some secret to be stored.

With AWS you can leverage on KMS + Policies and Roles to setup the access control and the permission to use encryption
key. Then part of the job is already done and can be automatised with cloudformation.

For the remaining part (provisioning the keymaterials and the retrieval from within the instance) you can use S3Vaultlib

Features
--------
The library let you store in an encrypted way, keymaterials into S3, by using server side encryption and different
keys per role.

The main feature of the library though, is the capability to abstract S3 in a way you can use it as key/value store or
blob store in jinja templates while you are provisioning your instance.

S3Vaultlib comes also with a simple cli, s3vaultcli that help to automate some simple tasks

S3Vaultlib implements also an ansible module to automate the template expansion within an Ansible deployment

Ansible Module
--------------
The library includes also a useful ansible module that allows you to easily create files from templates.
Check the following example:

template.j2::

    template test
    {{ nginx.server_name }}
    port: {{ nginx.port }}
    certificate:
    {{ cert }}
    htpasswd:
    {{ htpasswd }}
    environment:
    {{ ansible_env.PYENV_SHELL }}
    environment2:
    {{ environment['LOGNAME'] }}

playbook.yml::

    ---
    - name: test my new module
      connection: local
      hosts: localhost
      tasks:
        - name: test
          s3vault_template:
            bucket: 230706054651
            path: vault/nginx/
            kms_alias: gchiesa/testkey
            src: template.j2
            dest: outcome.txt
            ec2: false
            region: eu-west-1



This way the s3vault_template module will take the template, connect to S3, expose the filesystem as variables and you
use the files in your template


Example Use Case
----------------
We need to deploy a nginx instance, we need to provision a server name and a port dynamically and the htpasswd file
for basic authentication.

First of all we will have a KMS key with the name (nginx-key) for the role associated to the instance (nginx-role)

Now we provision the secrets in the vault with the cli:

* nginx configuration::

    s3vaultcli configset -b <bucket> -p vault/nginx -c nginx -K server_name -V www.example.com
    s3vaultcli configset -b <bucket> -p vault/nginx -c nginx -K server_port -V 8443

* htpasswd upload::

    s3vaultcli push -b <bucket> -p vault/nginx -s htpasswd -d htpasswd

*NOTE:* the library will try to detect the role and use a KMS key with the same alias of the role name. If we are in another
machine (or from our local machine we need to have access to the KMS key and specify the alias with the -k key_alias option)

In S3 now, we will have a structure like this::

    $ aws s3 ls s3://<bucket>/vault/nginx/
    2017-08-20 18:02:10          5 htpasswd
    2017-08-20 18:00:39         57 nginx

Now inside the instance we can prepare the templates to expand, for nginx.conf.j2 ::

    $ cat nginx.conf.j2
    server {
                    listen       {{ nginx.server_port }};
                    server_name  {{ nginx.server_name }};
                    access_log  logs/localhost.access.log  main;
                    location / {
                        root   html;
                        index  index.html index.htm;
                    }
            include /etc/nginx/sites-enabled/*;
            }
    }

And the htpasswd.j2::

    $ cat htpasswd.j2
    {{ htpasswd }}

When the instance starts in the userdata you can use the s3vaultcli tool to render the templates, in this way::

    s3vaultcli template -b <bucket> -p vault/nginx -t nginx.conf.j2 -d nginx.conf
    s3vaultcli template -b <bucket> -p vault/nginx -t htpasswd -d htpasswd


License
-------

* Free software: BSD license
* Documentation: https://s3vaultlib.readthedocs.io.


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

