import logging
log = logging.getLogger(__name__)


class SSHRPCManager(object):

	def __init__(self, settings):
		self.settings = settings

		# We can't use :0 because
		# A: It's quite hard to retrieve the port on the remote after the daemon has started
		# B: SSH doesn't accept 0:localhost:0 as a port forwarding option
		[self.local_server_port, self.local_callback_port] = self.getNPorts(2)
		[self.remote_server_port, self.remote_callback_port] = self.getNPorts(2)

	def getNPorts(self, n, port_range=(1024, 65535)):
		import random
		ports = []
		for i in range(0, n):
			while True:
				port = random.randrange(*port_range)
				if port not in ports:
					ports.append(port)
					break
		return ports

	def start(self):
		log.debug('Opening SSH connection')
		import subprocess

		ssh_cmd = ['ssh', '-i', self.settings['keyfile'],
		                  '-p', str(self.settings['port']),
		                  '-L' + str(self.local_server_port) + ':localhost:' + str(self.remote_server_port),
		                  '-R' + str(self.remote_callback_port) + ':localhost:' + str(self.local_callback_port),
		                  self.settings['username'] + '@' + self.settings['address'],
		                  '--',
		                  'sudo', self.settings['server_bin'],
		                  '--listen', str(self.remote_server_port)]
		import sys
		self.ssh_process = subprocess.Popen(args=ssh_cmd, stdout=sys.stderr, stderr=sys.stderr)

		# Check that we can connect to the server
		try:
			import Pyro4
			server_uri = 'PYRO:server@localhost:{server_port}'.format(server_port=self.local_server_port)
			self.rpc_server = Pyro4.Proxy(server_uri)

			log.debug('Connecting to the RPC daemon')
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
			self.ssh_process.terminate()
			raise e

	def stop(self):
		if hasattr(self, 'rpc_server'):
			log.debug('Stopping the RPC daemon')
			self.rpc_server.stop()
			self.rpc_server._pyroRelease()
		if hasattr(self, 'ssh_process'):
			log.debug('Waiting for the SSH connection to terminate')
			self.ssh_process.wait()
