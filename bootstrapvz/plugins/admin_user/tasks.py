from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks.initd import InstallInitScripts
from bootstrapvz.providers.ec2.tasks.initd import AddEC2InitScripts

import os
import logging
log = logging.getLogger(__name__)


class CheckPublicKeyFile(Task):
    description = 'Check that the public key is a valid file'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_call, rel_path

        pubkey = info.manifest.plugins['admin_user'].get('pubkey', None)
        if pubkey is not None:
            abs_pubkey = rel_path(info.manifest.path, pubkey)
            if not os.path.isfile(abs_pubkey):
                msg = 'Could not find public key at %s' % pubkey
                info.manifest.validation_error(msg, ['plugins', 'admin_user', 'pubkey'])

            ret, _, stderr = log_call('ssh-keygen -l -f ' + abs_pubkey)
            if ret != 0:
                msg = 'Invalid public key file at %s' % pubkey
                info.manifest.validation_error(msg, ['plugins', 'admin_user', 'pubkey'])


class AddSudoPackage(Task):
    description = 'Adding `sudo\' to the image packages'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('sudo')


class CreateAdminUser(Task):
    description = 'Creating the admin user'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root,
                        'useradd',
                        '--create-home', '--shell', '/bin/bash',
                        info.manifest.plugins['admin_user']['username']])


class PasswordlessSudo(Task):
    description = 'Allowing the admin user to use sudo without a password'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        sudo_admin_path = os.path.join(info.root, 'etc/sudoers.d/99_admin')
        username = info.manifest.plugins['admin_user']['username']
        with open(sudo_admin_path, 'w') as sudo_admin:
            sudo_admin.write('{username} ALL=(ALL) NOPASSWD:ALL'.format(username=username))
        import stat
        ug_read_only = (stat.S_IRUSR | stat.S_IRGRP)
        os.chmod(sudo_admin_path, ug_read_only)


class AdminUserPassword(Task):
    description = 'Setting the admin user password'
    phase = phases.system_modification
    predecessors = [InstallInitScripts, CreateAdminUser]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root, 'chpasswd'],
                       info.manifest.plugins['admin_user']['username'] +
                       ':' + info.manifest.plugins['admin_user']['password'])


class AdminUserPublicKey(Task):
    description = 'Installing the public key for the admin user'
    phase = phases.system_modification
    predecessors = [AddEC2InitScripts, CreateAdminUser]
    successors = [InstallInitScripts]

    @classmethod
    def run(cls, info):
        if 'ec2-get-credentials' in info.initd['install']:
            log.warn('You are using a static public key for the admin account.'
                     'This will conflict with the ec2 public key injection mechanism.'
                     'The ec2-get-credentials startup script will therefore not be enabled.')
            del info.initd['install']['ec2-get-credentials']

        # Get the stuff we need (username & public key)
        username = info.manifest.plugins['admin_user']['username']

        from bootstrapvz.common.tools import rel_path
        pubkey_path = rel_path(info.manifest.path,
                               info.manifest.plugins['admin_user']['pubkey'])

        with open(pubkey_path) as pubkey_handle:
            pubkey = pubkey_handle.read()

        # paths
        from os.path import join
        ssh_dir_rel   = join('home', username, '.ssh')
        auth_keys_rel = join(ssh_dir_rel, 'authorized_keys')
        ssh_dir_abs   = join(info.root, ssh_dir_rel)
        auth_keys_abs = join(info.root, auth_keys_rel)

        # Create the ssh dir if nobody has created it yet
        if not os.path.exists(ssh_dir_abs):
            os.mkdir(ssh_dir_abs, 0700)

        # Create (or append to) the authorized keys file (and chmod u=rw,go=)
        import stat
        with open(auth_keys_abs, 'a') as auth_keys_handle:
            auth_keys_handle.write(pubkey + '\n')
        os.chmod(auth_keys_abs, (stat.S_IRUSR | stat.S_IWUSR))

        # Set the owner of the authorized keys file
        # (must be through chroot, the host system doesn't know about the user)
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root,
                        'chown', '-R', (username + ':' + username), ssh_dir_rel])


class AdminUserPublicKeyEC2(Task):
    description = 'Modifying ec2-get-credentials to copy the ssh public key to the admin user'
    phase = phases.system_modification
    predecessors = [InstallInitScripts, CreateAdminUser]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import sed_i
        getcreds_path = os.path.join(info.root, 'etc/init.d/ec2-get-credentials')
        username = info.manifest.plugins['admin_user']['username']
        sed_i(getcreds_path, "username='root'", "username='{username}'".format(username=username))
