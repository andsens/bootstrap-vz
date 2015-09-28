from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks.initd import InstallInitScripts
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


class AdminUserCredentials(Task):
	description = 'Set up access credentials for the admin user'
	phase = phases.system_modification
	predecessors = [InstallInitScripts, CreateAdminUser]

	@classmethod
	def run(cls, info):
                from bootstrapvz.common.exceptions import TaskError
                from bootstrapvz.common.tools import sed_i
                from bootstrapvz.common.tools import log_check_call
                log = logging.getLogger(__name__)

                if 'password' in info.manifest.plugins['admin_user']:
                        if 'pubkey' in info.manifest.plugins['admin_user']:
                                msg = 'The options password and pubkey are mutually exclusive'
                                raise TaskError(msg)
                        log_check_call(['chroot', info.root, 'chpasswd'],
                                       info.manifest.plugins['admin_user']['username'] +
                                       ':' + info.manifest.plugins['admin_user']['password'])
                        return

                getcreds_path = os.path.join(info.root, 'etc/init.d/ec2-get-credentials')
                if 'pubkey' in info.manifest.plugins['admin_user']:
                        import stat
                        from shutil import copy
                        full_path = info.manifest.plugins['admin_user']['pubkey']
                        if not os.path.exists(full_path):
                                msg = 'Could not find public key at {full_path}'.format(full_path=full_path)
                                raise TaskError(msg)
                        log.debug('Copying public key from {path}'.format(path=full_path))

                        if os.path.exists(getcreds_path):
                                log.warn('You are using a static public key for the admin account.'
                                         ' This will conflict with the ec2 public key njection mechanisn.'
                                         ' The ec2-get-credentials startup script has therefore been disabled.')
                                log_check_call(['chroot', info.root, 'insserv', '--remove',
                                                'ec2-get-credentials'])
                        username = info.manifest.plugins['admin_user']['username']

                        ssh_file = os.path.join('/home/'
                                                '{username}/.ssh/authorized_keys'.format(username=username))
                        rel_ssh_file = os.path.realpath(info.root + '/{ssh_file}'.format(ssh_file=ssh_file))

                        ssh_dir = os.path.dirname(ssh_file)
                        rel_ssh_dir = os.path.realpath(info.root + '/{ssh_dir}'.format(ssh_dir=ssh_dir))
                        if not os.path.exists(rel_ssh_dir):
                                log.debug('Creating {ssh_dir} mode 700'.format(ssh_dir=rel_ssh_dir))
                                os.mkdir(rel_ssh_dir, 0700)
                        else:
				log.debug('setting {ssh_dir} mode 700'.format(ssh_dir=rel_ssh_dir))
                                os.chmod(rel_ssh_dir, 0700)
                        copy(full_path, rel_ssh_file)
                        mode = (stat.S_IRUSR | stat.S_IWUSR)
                        os.chmod(rel_ssh_file, mode)
                        log_check_call(['chroot', info.root, 'chown', '-R', username, ssh_dir])
                        return

                log.debug('Updating EC2 get credentials script.')
                username = info.manifest.plugins['admin_user']['username']
                sed_i(getcreds_path, 'username=\'root\'', 'username=\'{username}\''.format(username=username))
