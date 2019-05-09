.. _howto_nginx:

Configure NGINX with S3Vaultlib Ansible Plugin
==============================================

Let’s imagine a simple scenario where we need to deploy a nginx
instance. The instance is environment unaware and only at deploy time we
need to provision a server name and a port dynamically, and a
``htpasswd`` file for basic authentication.

Let’s also assume that the EC2 instance running NGINX will have the
``role_webserver`` associated (see :ref:`howto_provisioning_vault`)

Provisioning of keymaterials
----------------------------

-  We need to create a session as ``role_admin`` in order to provision
   the keymaterials and configuration

.. code:: bash

   s3vaultcli create_session -r role_admin --no-external-id

-  With the CLI we can provision a configuration file that holds the
   settings we need:

.. code:: bash

   s3vaultcli configset -b 'test-bucket-for-s3-vault' -p webserver -k role_webserver -c conf_nginx -K server_name -V www.example.com
   s3vaultcli configset -b 'test-bucket-for-s3-vault' -p webserver -k role_webserver -c conf_nginx -K server_port -V 8443

-  Now we push as separate keymaterial the ``htpasswd`` (prebuilt) file

.. code:: bash

   s3vaultcli push -b 'test-bucket-for-s3-vault' -p webserver -k role_webserver -s htpasswd -d htpasswd

**NOTE**\ *: if you don’t pass the kms_alias, the library will try to
detect the role and use a KMS key with the same alias of the role name.
If we are in another machine (or from our local machine we need to have
access to the KMS key and specify the alias with the -k key_alias
option)*

What’s now on S3 vault?
-----------------------

Let’s just stop a moment and see how the library actually implements the
vault. If we check S3 from AWS Console as privileged user (with S3 read
privileges) or with the aws CLI we will notice a structure like the
following:

::

   $ aws s3 ls s3://test-bucket-for-s3-vault/webserver/
   2017-08-20 18:02:10          5 htpasswd
   2017-08-20 18:00:39         57 conf_nginx

-  ``htpasswd`` has been saved as binary file via the push method
-  ``conf_nginx`` is a container (JSON file) that holds all the key and
   values set via the CLI. The JSON container will allow you to create
   very complex structure and retrieve them at runtime.

Prepare the configuration on EC2
--------------------------------

NGINX Conf
~~~~~~~~~~

Now we can prepare the templates to expand when the instance starts.
Best practice is to preallocate the templates in an EC2 AMI using Packer
by Hashicorp. Let’s create the file ``/opt/templates/nginx.conf.j2``
with the content:

.. code:: text

   server {
           listen {{ conf_nginx.server_port }} default_server;
           root /var/www/html;
           index index.html index.htm index.nginx-debian.html;
           server_name {{ conf_nging.server_name }};
           location / {
             root   html;
             index  index.html index.htm;
           }
   }

htpasswd
~~~~~~~~

Now inside the instance we can prepare the templates to expand when the
instance starts. Let’s create the file ``/opt/templates/htpasswd.j2``
with the content:

.. code:: text

   {{ htpasswd }}

EC2 Startup
-----------

Now we can launch an EC2 instance, keeping in mind the followings:

* We need to make sure the EC2 instance will use the pre-baked AMI generated
  with Packer
* We need to associate to the EC2 instance the role ``role_webserver``
* We need to setup the following command (beside the rest) in userdata

.. code:: bash

   s3vaultcli template -b 'test-bucket-for-s3-vault' -p webserver -t /opt/nginx.conf.j2 -d /etc/nginx/nginx.conf
   s3vaultcli template -b 'test-bucket-for-s3-vault' -p webserver -t htpasswd.j2 -d /etc/nginx/htpasswd
   chown nginx /etc/nginx/htpasswd && chmod go-rwx /etc/nginx/htpasswd


Ansible Support
---------------

Instead using ``s3vaultcli template`` we can also automate the provisioning of keymaterials
via the Ansible Action Plugin shipped together with the library.
The Ansible Plugin expose a new command ``s3vault_template``. The command has the same capabilities of the ``template``
command in Ansible with the additional feature that all the variables in the template are resolved using the Vault.

Example:

.. code:: yaml

    - name: Set nginx configuration
      s3vault_template:
        bucket: test-bucket-for-s3-vault
        path: webserver
        src: /opt/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        mode: 0600
        owner: nginx
        group: nginx

