from fysom import Fysom

import logging
log = logging.getLogger(__name__)


class SSHRPCManager(object):

	def __init__(self, settings):
		self.settings = settings

		import random
		self.local_server_port = random.randrange(1024, 65535)
		self.local_callback_port = random.randrange(1024, 65535)
		# self.remote_server_port = random.randrange(1024, 65535)
		# self.remote_callback_port = random.randrange(1024, 65535)
		self.remote_server_port = self.local_server_port
		self.remote_callback_port = self.local_callback_port

	def start(self):
		log.debug('Opening SSH connection')
		import subprocess

		ssh_cmd = ['ssh', '-i', self.settings['keyfile'],
		                  '-p', str(self.settings['port']),
		                  '-L' + str(self.local_server_port) + ':localhost:' + str(self.remote_server_port),
		                  '-R' + str(self.remote_callback_port) + ':localhost:' + str(self.local_callback_port),
		                  self.settings['username'] + '@' + self.settings['address'],
		                  '--',
		                  'sudo', self.settings['server-bin'],
		                  '--listen', str(self.remote_server_port)]
		import sys
		self.process = subprocess.Popen(args=ssh_cmd, stdout=sys.stderr, stderr=sys.stderr)

		# Check that we can connect to the server
		try:
			import Pyro4
			server_uri = 'PYRO:server@localhost:{server_port}'.format(server_port=self.local_server_port)
			self.rpc_server = Pyro4.Proxy(server_uri)

			log.debug('Connecting to PYRO')
			remaining_retries = 5
			while True:
				try:
					self.rpc_server.ping()
					break
				except (Pyro4.errors.ConnectionClosedError, Pyro4.errors.CommunicationError) as e:
					if remaining_retries > 0:
						remaining_retries -= 1
						from time import sleep
						sleep(2)
					else:
						raise e
		except (Exception, KeyboardInterrupt) as e:
			self.process.terminate()
			raise e

	def stop(self):
		self.rpc_server.stop()
		self.rpc_server._pyroRelease()
		self.process.wait()
