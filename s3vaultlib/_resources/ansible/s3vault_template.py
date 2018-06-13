#!/usr/bin/env python
import jinja2
import os
import copy
import logging
from ansible.module_utils.basic import AnsibleModule
from s3vaultlib.ec2metadata.ec2metadata import EC2Metadata
from s3vaultlib.connectionfactory.connectionfactory import ConnectionFactory
from s3vaultlib.s3vaultlib import S3Vault

logging.basicConfig(level=logging.DEBUG)

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: s3vault_template

short_description: Expand a template from a S3Vault

version_added: "2.4"

description:
    - "The module allow expand a template from s3vault"

        bucket=dict(type='str', required=True),
        path=dict(type='str', required=False, default='role/{{ role_name }}/encrypted'),
        kms_alias=dict(type='str', required=False),
        region=dict(type='str', required=True, default=None),
        profile=dict(type='str', required=False, default=None),
        src=dict(type='str', required=True),
        dest=dict(type='str', required=True),

options:
    bucket: 
        description:
            - The S3 bucket where the S3Vault resides
    path:
        description:
            - The path to use inside the bucket (note this path support variable expansion, like {{ role }} )
    kms_alias:
        description:
            - The KMS Alias to use to decrypt the data. If not specified the module will try to use the name of
              the role associate to the instance as KMS alias
    region:
        description:
            - The region to use
    profile: 
        description: 
            - Profile to use            
    mode: 
        description: 
            - Mode (numeric) to associate to the created destination file (default 0666)             
    owner: 
        description: 
            - User to associate to the created destination file             
    group: 
        description: 
            - Group to associate to the created destination file               
    src:        
        description: 
            - The source template to expand
    dest:        
        description: 
            - The destination file where to expand the template

author:
    - Giuseppe Chiesa (@gchiesa)
'''

EXAMPLES = '''
# Expand a template based on a configuration for nginx
- name: Expand nginx configuration
  s3vault_template:
    bucket: 123456789-vault
    region: eu-west-1
    src: /etc/nginx/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: Template: {src} expanded to: {dest}
'''


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        bucket=dict(type='str', required=True),
        path=dict(type='str', required=False, default='role/{{ role_name }}/encrypted'),
        kms_alias=dict(type='str', required=False),
        region=dict(type='str', required=False, default=None),
        profile=dict(type='str', required=False, default=None),
        src=dict(type='str', required=True),
        dest=dict(type='str', required=True),
        ec2=dict(type='bool', required=False, default=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        add_file_common_args=True,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # get the role
    if module.params['ec2']:
        ec2_metadata = EC2Metadata()
        template = jinja2.Template(module.params['path'])
        vault_path = template.render({'role_name': ec2_metadata.role})
    else:
        vault_path = module.params['path']

    conn_manager = ConnectionFactory(region=module.params['region'], profile_name=module.params['profile'])
    s3vault = S3Vault(module.params['bucket'], vault_path, connection_factory=conn_manager)

    ansible_env = copy.deepcopy(os.environ)
    environment = copy.deepcopy(os.environ)

    dest_path = os.path.dirname(os.path.abspath(module.params['dest']))
    dest_file = os.path.abspath(module.params['dest'])
    src_file = os.path.abspath(module.params['src'])
    if not os.access(dest_path, os.W_OK):
        module.fail_json(msg='Unable to write the destination file', **result)

    if not os.access(src_file, os.R_OK):
        module.fail_json(msg='Unable to read from the source file', **result)

    with open(dest_file, 'wb') as f_handler:
        f_handler.write(s3vault.render_template(src_file,
                                                ansible_env=ansible_env,
                                                environment=environment))

    file_args = module.load_file_common_arguments(module.params)
    # path is used for the s3 bucket so we will override with the dest file
    file_args['path'] = module.params['dest']
    result['changed'] = module.set_fs_attributes_if_different(file_args, result['changed'])
    result['message'] = 'Template: {src} expanded to: {dest}'.format(src=src_file,
                                                                     dest=dest_file)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
