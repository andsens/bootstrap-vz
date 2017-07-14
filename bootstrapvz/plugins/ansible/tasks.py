from bootstrapvz.base import Task
from bootstrapvz.common.tasks import host
from bootstrapvz.common import phases
from bootstrapvz.common.tools import rel_path
import os


class AddRequiredCommands(Task):
    description = 'Adding commands required for provisioning with ansible'
    phase = phases.validation
    successors = [host.CheckExternalCommands]

    @classmethod
    def run(cls, info):
        info.host_dependencies['ansible'] = 'ansible'

class CheckPlaybookPath(Task):
    description = 'Checking whether the playbook path exist'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.exceptions import TaskError
        playbook = rel_path(info.manifest.path, info.manifest.plugins['ansible']['playbook'])
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
    description = 'Running ansible playbook'
    phase = phases.user_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call

        # Extract playbook and directory
        playbook = rel_path(info.manifest.path, info.manifest.plugins['ansible']['playbook'])

        # build the inventory file
        inventory = os.path.join(info.root, 'tmp/bootstrap-inventory')
        with open(inventory, 'w') as handle:
            conn = '{} ansible_connection=chroot'.format(info.root)
            content = ""

            if 'hosts' in info.manifest.plugins['ansible']['hosts']:
                for host in info.manifest.plugins['ansible']['hosts']:
                    content += '[{}]\n{}\n'.format(host, conn)
            else:
                content = conn

            handle.write(content)

        # build the ansible command
        cmd = ['ansible-playbook', '-i', inventory, playbook]
        if 'extra_vars' in info.manifest.plugins['ansible']:
            tmp_cmd = ['--extra-vars', '\"{}\"'.format(info.manifest.plugins['ansible']['extra_vars'])]
            cmd.extend(tmp_cmd)
        if 'tags' in info.manifest.plugins['ansible']:
            tmp_cmd = ['--tags={}'.format(','.join(info.manifest.plugins['ansible']['tags']))]
            cmd.extend(tmp_cmd)
        if 'skip_tags' in info.manifest.plugins['ansible']:
            tmp_cmd = ['--skip-tags={}'.format(','.join(info.manifest.plugins['ansible']['skip_tags']))]
            cmd.extend(tmp_cmd)
        if 'opt_flags' in info.manifest.plugins['ansible']:
            # Should probably do proper validation on these, but I don't think it should be used very often.
            cmd.extend(info.manifest.plugins['ansible']['opt_flags'])

        # Run and remove the inventory file
        log_check_call(cmd)
        os.remove(inventory)
