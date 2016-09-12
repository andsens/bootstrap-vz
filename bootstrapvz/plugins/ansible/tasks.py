from bootstrapvz.base import Task
from bootstrapvz.common import phases
import os


class CheckPlaybookPath(Task):
    description = 'Checking whether the playbook path exist'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.exceptions import TaskError
        playbook = info.manifest.plugins['ansible']['playbook']
        if not os.path.exists(playbook):
            msg = 'The playbook file {playbook} does not exist.'.format(playbook=playbook)
            raise TaskError(msg)
        if not os.path.isfile(playbook):
            msg = 'The playbook path {playbook} does not point to a file.'.format(playbook=playbook)
            raise TaskError(msg)


class AddPackages(Task):
    description = 'Making sure python is installed'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('python')


class RunAnsiblePlaybook(Task):
    description = 'Running ansible playbooks'
    phase = phases.user_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call

        # Extract playbook and directory
        playbook = info.manifest.plugins['ansible']['playbook']
        playbook_dir = os.path.dirname(os.path.realpath(playbook))

        # Check for hosts
        hosts = None
        if 'hosts' in info.manifest.plugins['ansible']:
            hosts = info.manifest.plugins['ansible']['hosts']

        # Check for extra vars
        extra_vars = None
        if 'extra_vars' in info.manifest.plugins['ansible']:
            extra_vars = info.manifest.plugins['ansible']['extra_vars']

        tags = None
        if 'tags' in info.manifest.plugins['ansible']:
            tags = info.manifest.plugins['ansible']['tags']

        skip_tags = None
        if 'skip_tags' in info.manifest.plugins['ansible']:
            skip_tags = info.manifest.plugins['ansible']['skip_tags']

        opt_flags = None
        if 'opt_flags' in info.manifest.plugins['ansible']:
            opt_flags = info.manifest.plugins['ansible']['opt_flags']

        # build the inventory file
        inventory = os.path.join(info.root, 'tmp/bootstrap-inventory')
        with open(inventory, 'w') as handle:
            conn = '{} ansible_connection=chroot'.format(info.root)
            content = ""

            if hosts:
                for host in hosts:
                    content += '[{}]\n{}\n'.format(host, conn)
            else:
                content = conn

            handle.write(content)

        # build the ansible command
        cmd = ['ansible-playbook', '-i', inventory, os.path.basename(playbook)]
        if extra_vars:
            tmp_cmd = ['--extra-vars', '\"{}\"'.format(extra_vars)]
            cmd.extend(tmp_cmd)
        if tags:
            tmp_cmd = ['--tags={}'.format(tags)]
            cmd.extend(tmp_cmd)
        if skip_tags:
            tmp_cmd = ['--skip_tags={}'.format(skip_tags)]
            cmd.extend(tmp_cmd)
        if opt_flags:
            # Should probably do proper validation on these, but I don't think it should be used very often.
            cmd.extend(opt_flags)

        # Run and remove the inventory file
        log_check_call(cmd, cwd=playbook_dir)
        os.remove(inventory)
