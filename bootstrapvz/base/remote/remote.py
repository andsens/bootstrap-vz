"""Main module containing all the setup necessary for running the remote bootstrapping process
"""


def main():
	"""Main function for invoking the bootstrap process remotely


	"""
	# Get the commandline arguments
	opts = get_opts()

	# Load the manifest
	from bootstrapvz.base.manifest import Manifest
	manifest = Manifest(path=opts['MANIFEST'])

	# Load the build servers
	from bootstrapvz.common.tools import load_data
	build_servers = load_data(opts['--servers'])

	# Set up logging
	from bootstrapvz.base.main import setup_loggers
	setup_loggers(opts)

	# Register deserialization handlers for objects
	# that will pass between server and client
	from . import register_deserialization_handlers
	register_deserialization_handlers()

	# Everything has been set up, connect to the server and begin the bootstrapping process
	run(manifest,
	    build_servers[opts['SERVER']],
	    debug=opts['--debug'],
	    dry_run=opts['--dry-run'])


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


def run(manifest, server, debug=False, dry_run=False):
	"""Connects to the remote build server, starts an RPC daemin
	on the other side and initiates a remote bootstrapping procedure
	"""
	bootstrap_info = None

	from ssh_rpc_manager import SSHRPCManager
	manager = SSHRPCManager(server)
	try:
		# Connect to the build server and start the RPC daemon
		manager.start()
		server = manager.rpc_server
		# Start a callback server on this side, so that we may receive log entries
		from callback import CallbackServer
		callback_server = CallbackServer(listen_port=manager.local_callback_port,
		                                 remote_port=manager.remote_callback_port)
		from bootstrapvz.base.log import LogServer
		log_server = LogServer()
		try:
			# Start the callback server (in a background thread)
			callback_server.start(log_server)
			# Tell the RPC daemon about the callback server
			server.set_log_server(log_server)

			# Everything has been set up, begin the bootstrapping process
			bootstrap_info = server.run(manifest,
			                            debug=debug,
			                            # We can't pause the bootstrapping process remotely, yet...
			                            pause_on_error=False,
			                            dry_run=dry_run)
		finally:
			# Stop the callback server
			callback_server.stop()
	finally:
		# Stop the RPC daemon and close the SSH connection
		manager.stop()
	return bootstrap_info
