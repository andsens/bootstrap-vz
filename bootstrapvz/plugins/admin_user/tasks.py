from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks.initd import InstallInitScripts
from bootstrapvz.providers.ec2.tasks.initd import AddEC2InitScripts

import logging
import os


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


class AdminUserCredentialsPassword(Task):
        description = 'Set up access credentials for the admin user with a given password'
        phase = phases.system_modification
        predecessors = [InstallInitScripts, CreateAdminUser]

        @classmethod
        def run(cls, info):
                from bootstrapvz.common.tools import log_check_call
                log = logging.getLogger(__name__)

                log.debug('Setting the password for the admin user.')
                log_check_call(['chroot', info.root, 'chpasswd'],
                               info.manifest.plugins['admin_user']['username'] +
                               ':' + info.manifest.plugins['admin_user']['password'])
                return


class AdminUserCredentialsPublicKey(Task):
        description = 'Set up access credentials for the admin user with a given public key'
        phase = phases.system_modification
        predecessors = [AddEC2InitScripts, CreateAdminUser]
        successors = [InstallInitScripts]

        @classmethod
        def run(cls, info):
                from bootstrapvz.common.tools import log_check_call

                log = logging.getLogger(__name__)

                import stat
                from shutil import copy
                full_path = info.manifest.plugins['admin_user']['pubkey']
                log.debug('Copying public key from {path}'.format(path=full_path))

                if 'ec2-get-credentials' in info.initd['install']:
                        log.warn('You are using a static public key for the admin account.'
                                 ' This will conflict with the ec2 public key injection mechanisn.'
                                 ' The ec2-get-credentials startup script has therefore been disabled.')
                        del info.initd['install']['ec2-get-credentials']

                username = info.manifest.plugins['admin_user']['username']

                ssh_file = os.path.join('/home/', username, '/.ssh/authorized_keys')
                rel_ssh_file = os.path.realpath(info.root + '/%s' % ssh_file)

                ssh_dir = os.path.dirname(ssh_file)
                rel_ssh_dir = os.path.realpath(info.root + '/%s' % ssh_dir)
                if not os.path.exists(rel_ssh_dir):
                        log.debug('Creating %s mode 700' % rel_ssh_dir)
                        os.mkdir(rel_ssh_dir, 0700)
                else:
                        log.debug('setting %s mode 700' % rel_ssh_dir)
                        os.chmod(rel_ssh_dir, 0700)
                copy(full_path, rel_ssh_file)
                mode = (stat.S_IRUSR | stat.S_IWUSR)
                os.chmod(rel_ssh_file, mode)
                log_check_call(['chroot', info.root, 'chown', '-R', username, ssh_dir])
                return


class AdminUserCredentialsEC2(Task):
        description = 'Set up access credentials for the admin user using the EC2 credentials'
        phase = phases.system_modification
        predecessors = [InstallInitScripts, CreateAdminUser]

        @classmethod
        def run(cls, info):
                from bootstrapvz.common.exceptions import TaskError
                from bootstrapvz.common.tools import sed_i
                log = logging.getLogger(__name__)

                getcreds_path = os.path.join(info.root, 'etc/init.d/ec2-get-credentials')
                if os.path.exists(getcreds_path):
                        log.debug('Updating EC2 get credentials script.')
                        username = info.manifest.plugins['admin_user']['username']
                        sed_i(getcreds_path, "username='root'",
                              "username='{username}'".format(username=username))
                else:
                        raise TaskError('Could not find EC2 get credentials script.')
