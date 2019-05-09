.. _architecture:

Architecture
============

The following diagram show the overall architecture of the S3Vaultlib

::

    +----------------------------+---------------------------+
    |                            |                           |
    |       S3Vaultcli           |       S3VaultEditor       |
    |                            |                           |
    +----------------------------+---------------------------+
    |                                                        |
    |                        S3Vault                         |
    |                                                        |
    +--------------------------------------------------------+
    |         |                                  | EC2       |
    |KMS      | S3Fs                             | Metadata  |
    |Resolver | (manage low level JSON objects)  | Retriever |
    +---------+----------------------------------+-----------+
              |                                  |
              |              AWS S3              |
              |                                  |
              +----------------------------------+

* | **S3Fs** is the layer that abstracts the object management on S3 with ServerSide Encryption
* | **KMS Resolver** is an helper that resolves the KMS Key from the role of from aliases
* | **EC2 Metadata Retriever** is an helper that tries to lookup the role when the tool is used
  | inside a AWS resource
* | **S3Vault** is the main library that export high level APIs to be used in other applications
* | **S3Vaultcli** is the Command Line Interface
* | **S3VaultEditor** is the inline and in memory editor to change the content of the vault
  | objects
