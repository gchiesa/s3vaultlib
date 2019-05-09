.. _cli_usage:

Command Line Interface: s3vaultcli
==================================

S3Vaultlib ships also a powerful command line interface to interact with
several functionalities

General Help
------------

To check the latest version of the features and command available the
inline help is the main reference

.. code:: bash

   s3vaultcli --help

for each subcommand you can get detailed help with:

.. code:: bash

   s3vaultcli <command> --help

Vault Provisioning
------------------

Create S3Vault Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command creates an example of the YAML configuration that is the
starting point to provision a Vault

**example**:

.. code:: bash

    s3vaultcli create_s3vault_config --output vault.yml

Create Cloudformation
~~~~~~~~~~~~~~~~~~~~~

This command generate the cloudformation based on the Vault YAML
configuration.

**example**:

.. code:: bash

   s3vaultcli create_cloudformation --config vault.yml --output vault.template

Vault objects management
------------------------

Push
~~~~

Upload a object in the Vault

**example**:

.. code:: bash

   s3vaultcli push -b my_bucket_example -p webserver -k role_webserver -s mycert_key -d mycert_key

**NOTE**: *please notice that S3Vaultlib does not
support dots(.) in the objects to push to the vault*

Get
~~~

Retrieve a object from the Vault

**example**:

.. code:: bash

   s3vaultcli get -b my_bucket_example -p webserver -k role_webserver -s mycert_key -d mycert_key

**example**: from an EC2 instance with the role **role_webserver**
associated

.. code:: bash

   s3vaultcli get -b my_bucket_example -p webserver -s mycert_key -d mycert_key

**NOTE**: *if there is a role associated in the instance where the
s3vaultcli perform a call, S3Vaultlib will try to detect the role name
and then use the alias with the same name as the role*

Configuration Set
~~~~~~~~~~~~~~~~~

Create or update a configuration object in the Vault

**example**:

.. code:: bash

   s3vaultcli configset -b my_bucket_example -p webserver -k role_webserver -c conf_nginx -K server_name -V www.example.com

S3Vaultcli can also create more complex objects and hierarchies. Like
the following example:

**example**: create a list object with the key ``routed_network`` inside
the configuration object conf_vpn

.. code:: bash

   s3vaultcli configset -b my_bucket_example -p webserver -k role_webserver -c conf_vpn -K routed_networks -V '192.168.10.0/24, 192.168.11.0/24' -T list 

S3Vaultcli can also attach a JSON or YAML object directly as subkey

**example**: create a sub object with the content of the YAML file
``data.yml`` inside the configuration object conf_vpn

.. code:: bash

   s3vaultcli configset -b my_bucket_example -p webserver -k role_webserver -c conf_vpn -K routed_networks -V data.yml -T yaml

Configuration Edit
~~~~~~~~~~~~~~~~~~

This command will open a configuration editor inline (and in memory
only) to dynamically view/change the content of a configuration object.
The editor is quite powerful, supports **realtime validation** of the
format (JSON/YAML) and **syntax highlighting**.

**example**: edit the configuration for the ``conf_vpn`` object as YAML
file in memory

.. code:: bash

   s3vaultcli configedit -b my_bucket_example -p webserver -k role_webserver -c conf_vpn -t yaml

Template Expansion
------------------

Template
~~~~~~~~

This command parse a Jinja2 template file and expands the jinja2
variables by retriving the information from the Vault

**example**:

.. code:: bash

   s3vaultcli template -b my_bucket_example -p webserver -k role_webserver -t template.j2 -d output.txt

**NOTE**: for more example see the :ref:`Configure NGINX with S3Vaultlib
Ansible Plugin<howto_nginx>`

Ansible support
~~~~~~~~~~~~~~~

In order to be able to use / load the plugin for ansible you should
export the ansible role shipped with s3vaultlib in the role_path in
ansible:

**example**:

.. code:: bash

   s3vaultcli ansible_path
