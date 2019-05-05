# S3Vaultlib

S3Vaultlib is a Python Library and CLI tool that enable you to implements a secure vault / configuration datastore for your AWS platform by using AWS resources: CloudFormation, S3, IAM, KMS
S3Vaultlib it's __yet another vault__ with the goal to give easy maintainability, use only AWS resource and with strong security patterns in mind.

# Why a vault?
It's a common pattern in SRE and DevSecOps to create resources environment unaware and configure the resource automatically when is deployed in a specific environment


# S3Vaultlib Features
* Use Server Side Encryption to store the objects on S3 with per-role KMS key

* Use per role encryption with least privilege patterns to access the vault. Each role in the vault __can only consume__ its own keymaterials 

* Special elevated privileged mode with a specific role able to produce and configure keymaterials, with only temporary access 

* Save, retrieve, update objects in the vault

* Integrates flawlessly with Ansible by exposing an action plugin that allows you to expand templates by using variables / keymaterials from the vault

* Powerful CLI to create, manage and update the objects in the vault

* Easy maintainable via simple yaml file

* Expose a flexyble python library to extend functionalities or implement the retrieval of keymaterials from your code.


# S3vaultlib Architecture
__S3Vaultlib requires no installation or security patches / updates.__ The architecture leverages entirely on AWS existing resource to create a secure vault with Role Base Access Control, versioning and region awareness.

It integrates with the __IAM__ to generate the necessary roles and policies, __KMS__ to generate per-role keys, __S3__ to configure the bucket policies to enforce high level of security and __CloudFormation__ to create the Infrastructure as Code that combine all the above in a powerful vault.

Check [In depth Architecture] for more information

# Usage 
## Example scenarios
* [Configure NGINX with S3Vaultlib Ansible Plugin]
  A simple example where we deploy an environment unaware NGINX instance and it's configured via S3Vaultlib ansible plugin
  
## Documentation
The complete documentation can be found [here]

# Alternatives 
Currently there are several alternative patterns used. 

* Configuration / Keymaterials encrypted in git  
  __Please don't do this, really!__

* [Vault] by Hashicorp  
  Full featured vault system, widely used in the DevOPS community. But it's also yet another system to deploy and maintain in high availability and also, it requires keymaterials for the installation (since is not a native AWS component)

* [AWS Secret Manager]  
  Very valid alternative offered by AWS. Still lack a bit of flexibility to be used transparently in your bootstrap pipelines for EC2 / Dockers / Lambdas / Applications

[Vault]: https://www.vaultproject.io/
[AWS Secret Manager]: https://aws.amazon.com/secrets-manager/
