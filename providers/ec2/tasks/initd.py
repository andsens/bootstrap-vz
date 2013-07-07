from base import Task
from common import phases
import os.path


class ResolveInitScripts(Task):
	description = 'Determining which startup scripts to install or disable'
	phase = phases.system_modification

	def run(self, info):
		init_scripts = {'ec2-get-credentials': 'ec2-get-credentials',
		                'ec2-run-user-data': 'ec2-run-user-data',
		                'expand-volume': 'expand-volume'}

		init_scripts['generate-ssh-hostkeys'] = 'generate-ssh-hostkeys'
		if info.manifest.system['release'] == 'squeeze':
			init_scripts['generate-ssh-hostkeys'] = 'squeeze/generate-ssh-hostkeys'

		disable_scripts = ['hwclock.sh']
		if info.manifest.system['release'] == 'squeeze':
			disable_scripts.append('hwclockfirst.sh')

		for name, path in init_scripts.iteritems():
			init_scripts[name] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/init.d', path))

		info.initd = {'install': init_scripts,
		              'disable': disable_scripts}


class InstallInitScripts(Task):
	description = 'Installing startup scripts'
	phase = phases.system_modification
	after = [ResolveInitScripts]

	def run(self, info):
		import stat
		rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		             stat.S_IRGRP                | stat.S_IXGRP |
		             stat.S_IROTH                | stat.S_IXOTH)
		from shutil import copy
		from common.tools import log_check_call
		for name, src in info.initd['install'].iteritems():
			dst = os.path.join(info.root, 'etc/init.d', name)
			copy(src, dst)
			os.chmod(dst, rwxr_xr_x)
			log_check_call(['chroot', info.root, '/sbin/insserv', '-d', name])

		for name in info.initd['disable']:
			log_check_call(['chroot', info.root, '/sbin/insserv', '-r', name])
