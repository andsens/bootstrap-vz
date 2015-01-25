from build_server import BuildServer
from bootstrapvz.common.tools import log_check_call
import logging
log = logging.getLogger(__name__)


class RemoteBuildServer(BuildServer):

	def __init__(self, name, settings):
		super(RemoteBuildServer, self).__init__(name, settings)
		self.address = settings['address']
		self.port = settings['port']
		self.username = settings['username']
		self.password = settings.get('password', None)
		self.keyfile = settings['keyfile']
		self.server_bin = settings['server_bin']

		from . import getNPorts
		# We can't use :0 for the forwarding ports because
		# A: It's quite hard to retrieve the port on the remote after the daemon has started
		# B: SSH doesn't accept 0:localhost:0 as a port forwarding option
		[self.local_server_port, self.local_callback_port] = getNPorts(2)
		[self.remote_server_port, self.remote_callback_port] = getNPorts(2)

	def connect(self):
		log.debug('Opening SSH connection to build server `{name}\''.format(name=self.name))
		import subprocess

		server_cmd = ['sudo', self.server_bin, '--listen', str(self.remote_server_port)]

		def set_process_group():
			# Changes the process group of a command so that any SIGINT
			# for the main thread will not be propagated to it.
			# We'd like to handle SIGINT ourselves (i.e. propagate the shutdown to the serverside)
			import os
			os.setpgrp()

		addr_arg = '{user}@{host}'.format(user=self.username, host=self.address)
		ssh_cmd = ['ssh', '-i', self.keyfile,
		                  '-p', str(self.port),
		                  '-L' + str(self.local_server_port) + ':localhost:' + str(self.remote_server_port),
		                  '-R' + str(self.remote_callback_port) + ':localhost:' + str(self.local_callback_port),
		                  addr_arg]
		full_cmd = ssh_cmd + ['--'] + server_cmd
		import sys
		self.ssh_process = subprocess.Popen(args=full_cmd, stdout=sys.stderr, stderr=sys.stderr,
		                                    preexec_fn=set_process_group)

		# Check that we can connect to the server
		try:
			import Pyro4
			server_uri = 'PYRO:server@localhost:{server_port}'.format(server_port=self.local_server_port)
			self.connection = Pyro4.Proxy(server_uri)

			log.debug('Connecting to the RPC daemon on build server `{name}\''.format(name=self.name))
			remaining_retries = 5
			while True:
				try:
					self.connection.ping()
					break
				except (Pyro4.errors.ConnectionClosedError, Pyro4.errors.CommunicationError):
					if remaining_retries > 0:
						remaining_retries -= 1
						from time import sleep
						sleep(2)
					else:
						raise
		except (Exception, KeyboardInterrupt):
			self.ssh_process.terminate()
			raise
		return self.connection

	def disconnect(self):
		if hasattr(self, 'connection'):
			log.debug('Stopping the RPC daemon on build server `{name}\''.format(name=self.name))
			self.connection.stop()
			self.connection._pyroRelease()
		if hasattr(self, 'ssh_process'):
			log.debug('Waiting for SSH connection to build server `{name}\' to terminate'.format(name=self.name))
			self.ssh_process.wait()

	def download(self, src, dst):
		log.debug('Downloading file `{src}\' from '
		          'build server `{name}\' to `{dst}\''
		          .format(src=src, dst=dst, name=self.name))
		# Make sure we can read the file as {user}
		self._remote_command(['sudo', 'chown', self.username, src])
		src_arg = '{user}@{host}:{path}'.format(user=self.username, host=self.address, path=src)
		log_check_call(['scp', '-i', self.keyfile, '-P', str(self.port),
		                src_arg, dst])

	def delete(self, path):
		log.debug('Deleting file `{path}\' on build server `{name}\''.format(path=path, name=self.name))
		self._remote_command(['sudo', 'rm', path])

	def _remote_command(self, command):
		ssh_cmd = ['ssh', '-i', self.keyfile,
		                  '-p', str(self.port),
		                  self.username + '@' + self.address,
		                  '--'] + command
		log_check_call(ssh_cmd)

	def run(self, manifest):
		from bootstrapvz.remote.main import run
		return run(manifest, self)
