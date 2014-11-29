from bootstrapvz.common.tools import log_check_call


class BuildServer(object):

	def __init__(self, settings):
		self.settings = settings
		self.build_settings = settings.get('build_settings', None)
		self.can_bootstrap = settings['can_bootstrap']
		self.release = settings.get('release', None)


class LocalBuildServer(BuildServer):
	pass


class RemoteBuildServer(BuildServer):

	def __init__(self, settings):
		self.address = settings['address']
		self.port = settings['port']
		self.username = settings['username']
		self.password = settings['password']
		self.root_password = settings['root_password']
		self.keyfile = settings['keyfile']
		self.server_bin = settings['server_bin']
		super(RemoteBuildServer, self).__init__(settings)

	def download(self, src, dst):
		src_arg = '{user}@{host}:{path}'.format(self.username, self.address, src)
		log_check_call(['scp', '-i', self.keyfile, '-P', self.port,
		                src_arg, dst])

	def delete(self, path):
		ssh_cmd = ['ssh', '-i', self.settings['keyfile'],
		                  '-p', str(self.settings['port']),
		                  self.username + '@' + self.address,
		                  '--',
		                  'sudo', 'rm', path]
		log_check_call(ssh_cmd)
