"""Remote module containing methods to bootstrap remotely
"""


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

	register_deserialization_handlers()

	bootstrap_info = None

	from ssh_rpc_manager import SSHRPCManager
	manager = SSHRPCManager(build_servers[opts['SERVER']])
	try:
		manager.start()
		server = manager.rpc_server
		from callback import CallbackServer
		callback_server = CallbackServer(manager.local_callback_port)
		from bootstrapvz.base.log import LogServer
		log_server = LogServer()
		try:
			callback_server.start(log_server)
			server.set_log_server(log_server)

			# Everything has been set up, begin the bootstrapping process
			bootstrap_info = server.run(manifest,
			                            debug=opts['--debug'],
			                            pause_on_error=False,
			                            dry_run=opts['--dry-run'])
		finally:
			callback_server.stop()
	finally:
		manager.stop()
	return bootstrap_info


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


def register_deserialization_handlers():
	from Pyro4.util import SerializerBase
	SerializerBase.register_dict_to_class('bootstrapvz.base.manifest.Manifest', deserialize_manifest)
	SerializerBase.register_dict_to_class('bootstrapvz.base.bootstrapinfo.BootstrapInformation', deserialize_bootstrapinfo)


def deserialize_manifest(classname, state):
	from bootstrapvz.base.manifest import Manifest
	return Manifest(path=state['path'], data=state['data'])


def deserialize_bootstrapinfo(classname, state):
	from bootstrapvz.base.bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation.__new__(BootstrapInformation)
	bootstrap_info.__setstate__(state)
	return bootstrap_info
