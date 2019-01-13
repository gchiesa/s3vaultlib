from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import shutil
import tempfile
import jinja2
from ansible.errors import AnsibleError, AnsibleFileNotFound
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.template import generate_ansible_template_vars
from s3vaultlib.ec2metadata.ec2metadata import EC2Metadata
from s3vaultlib.connectionfactory.connectionfactory import ConnectionFactory
from s3vaultlib.s3vaultlib import S3Vault

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class ActionModule(ActionBase):

    TRANSFERS_FILES = True
    DEFAULT_NEWLINE_SEQUENCE = "\n"

    def get_checksum(self, dest, all_vars, try_directory=False, source=None, tmp=None):
        try:
            dest_stat = self._execute_remote_stat(dest, all_vars=all_vars, follow=False, tmp=tmp)

            if dest_stat['exists'] and dest_stat['isdir'] and try_directory and source:
                base = os.path.basename(source)
                dest = os.path.join(dest, base)
                dest_stat = self._execute_remote_stat(dest, all_vars=all_vars, follow=False, tmp=tmp)

        except AnsibleError as e:
            return dict(failed=True, msg=to_text(e))

        return dest_stat['checksum']

    def run(self, tmp=None, task_vars=None):
        """ handler for template operations """
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        bucket = self._task.args.get('bucket', None)
        path = self._task.args.get('path', 'role/{{ role_name }}/encrypted')
        # kms_alias = self._task.args.get('kms_alias', None)
        region = self._task.args.get('region', None)
        profile = self._task.args.get('profile', None)
        ec2 = self._task.args.get('ec2', True)

        src = self._task.args.get('src', None)
        dest = self._task.args.get('dest', None)

        # force = boolean(self._task.args.get('force', True), strict=False)
        follow = boolean(self._task.args.get('follow', False), strict=False)
        state = self._task.args.get('state', None)
        newline_sequence = self._task.args.get('newline_sequence', self.DEFAULT_NEWLINE_SEQUENCE)
        # variable_start_string = self._task.args.get('variable_start_string', None)
        # variable_end_string = self._task.args.get('variable_end_string', None)
        # block_start_string = self._task.args.get('block_start_string', None)
        # block_end_string = self._task.args.get('block_end_string', None)
        # trim_blocks = self._task.args.get('trim_blocks', None)

        wrong_sequences = ["\\n", "\\r", "\\r\\n"]
        allowed_sequences = ["\n", "\r", "\r\n"]

        # We need to convert unescaped sequences to proper escaped sequences for Jinja2
        if newline_sequence in wrong_sequences:
            newline_sequence = allowed_sequences[wrong_sequences.index(newline_sequence)]

        if state is not None:
            result['failed'] = True
            result['msg'] = "'state' cannot be specified on a template"
        elif src is None or dest is None:
            result['failed'] = True
            result['msg'] = "src and dest are required"
        elif bucket is None:
            result['failed'] = True
            result['msg'] = "bucket is required"
        elif newline_sequence not in allowed_sequences:
            result['failed'] = True
            result['msg'] = "newline_sequence needs to be one of: \n, \r or \r\n"
        else:
            try:
                src = self._find_needle('templates', src)
            except AnsibleError as e:
                result['failed'] = True
                result['msg'] = to_text(e)

        if 'failed' in result:
            return result

        # Get vault decrypted tmp file
        try:
            tmp_source = self._loader.get_real_file(src)
        except AnsibleFileNotFound as e:
            result['failed'] = True
            result['msg'] = "could not find src=%s, %s" % (src, e)
            self._remove_tmp_path(tmp)
            return result

        # template the source data locally & get ready to transfer
        try:
            # with open(tmp_source, 'r') as f:
            #     template_data = to_text(f.read())

            # add ansible 'template' vars
            temp_vars = task_vars.copy()
            temp_vars.update(generate_ansible_template_vars(src))

            # get the role
            if ec2:
                ec2_metadata = EC2Metadata()
                template = jinja2.Template(path)
                vault_path = template.render({'role_name': ec2_metadata.role})
            else:
                vault_path = path

            conn_manager = ConnectionFactory(region=region, profile_name=profile)
            s3vault = S3Vault(bucket, vault_path, connection_factory=conn_manager)

            resultant = s3vault.render_template(tmp_source, **temp_vars)
        except Exception as e:
            result['failed'] = True
            result['msg'] = "%s: %s" % (type(e).__name__, to_text(e))
            return result
        finally:
            self._loader.cleanup_tmp_file(tmp_source)

        new_task = self._task.copy()
        # remove unsupported variables
        new_task.args.pop('newline_sequence', None)
        new_task.args.pop('block_start_string', None)
        new_task.args.pop('block_end_string', None)
        new_task.args.pop('variable_start_string', None)
        new_task.args.pop('variable_end_string', None)
        new_task.args.pop('trim_blocks', None)
        new_task.args.pop('bucket', None)
        new_task.args.pop('kms_alias', None)
        new_task.args.pop('path', None)
        tempdir = tempfile.mkdtemp()
        try:
            result_file = os.path.join(tempdir, os.path.basename(src))
            with open(result_file, 'wb') as f:
                f.write(to_bytes(resultant, errors='surrogate_or_strict'))

            new_task.args.update(
                dict(
                    src=result_file,
                    dest=dest,
                    follow=follow,
                ),
            )
            copy_action = self._shared_loader_obj.action_loader.get('copy',
                                                                    task=new_task,
                                                                    connection=self._connection,
                                                                    play_context=self._play_context,
                                                                    loader=self._loader,
                                                                    templar=self._templar,
                                                                    shared_loader_obj=self._shared_loader_obj)
            result.update(copy_action.run(task_vars=task_vars))
        finally:
            shutil.rmtree(tempdir)

        return result
