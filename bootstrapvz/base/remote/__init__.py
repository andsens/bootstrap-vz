import Pyro4
from threading import Thread
"""Remote module containing methods to bootstrap remotely
"""


import logging
log = logging.getLogger(__name__)

stop = False


def main():
	"""Main function for invoking the bootstrap process remotely
	"""
	# Get the commandline arguments
	opts = get_opts()

	# Load the manifest
	from bootstrapvz.base.manifest import Manifest
	manifest = Manifest(path=opts['MANIFEST'])

	from bootstrapvz.common.tools import load_data
	build_servers = load_data(opts['--servers'])

	# Set up logging
	from bootstrapvz.base.main import setup_loggers
	setup_loggers(opts)

	from ssh_rpc_manager import SSHRPCManager
	manager = SSHRPCManager(build_servers[opts['SERVER']])
	try:
		manager.start()
		server = manager.rpc_server

		# Everything has been set up, begin the bootstrapping process
		print('run')
		server.run(None,
		           debug=opts['--debug'],
		           pause_on_error=False,
		           dry_run=opts['--dry-run'])
		print('hasrun')
	finally:
		manager.stop()


def get_opts():
	"""Creates an argument parser and returns the arguments it has parsed
	"""
	from docopt import docopt
	usage = """bootstrap-vz-remote

Usage: bootstrap-vz-remote [options] --servers=<path> SERVER MANIFEST

Options:
  --servers <path>   Path to list of build servers
  --log <path>       Log to given directory [default: /var/log/bootstrap-vz]
                     If <path> is `-' file logging will be disabled.
  --pause-on-error   Pause on error, before rollback
  --dry-run          Don't actually run the tasks
  --debug            Print debugging information
  -h, --help         show this help
	"""
	return docopt(usage)


def setup_interrupt_server(manager):

	def on_error(e):
		raw_input('Press Enter to commence rollback')
		return True

	daemon = Pyro4.Daemon()
	daemon.register(on_error)

	def serve():
		daemon.requestLoop(loopCondition=lambda: manager.current == 'rpc_started')

	thread = Thread(target=serve)
	thread.start()
	return (thread, on_error)


def setup_log_server(manager):
	from log import LogServer
	log_server = LogServer()
	daemon = Pyro4.Daemon()
	daemon.register(log_server)

	def serve():
		def check():
			import logging
			log = logging.getLogger(__name__)
			log.info(stop)
			return not stop
		daemon.requestLoop(loopCondition=check)

	thread = Thread(target=serve)
	thread.start()
	return (thread, log_server)
