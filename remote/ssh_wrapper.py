

class RemoteServer(object):

	def __init__(self):
		import random
		self.server_port = random.randrange(1024, 65535)
		self.client_port = random.randrange(1024, 65535)

	def start(self):
		import subprocess

		command = ['ssh', '-i', '/Users/anders/.vagrant.d/insecure_private_key',
		                  '-t',  # Force pseudo-tty allocation so that server.py quits when we close the connection
		                  '-p', '2222',
		                  '-L' + str(self.server_port) + ':localhost:' + str(self.server_port),
		                  '-R' + str(self.client_port) + ':localhost:' + str(self.client_port),
		                  'vagrant@localhost',
		                  '--',
		                  'sudo', '/root/bootstrap/remote/server.py',
		                  '--listen-port', str(self.server_port),
		                  '--callback-port', str(self.client_port)]
		self.process = subprocess.Popen(args=command)
		import time
		time.sleep(2)

	def stop(self):
		self.process.terminate()
