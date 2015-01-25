"""Main module containing all the setup necessary for running the remote bootstrapping process
"""


def main():
	"""Main function for invoking the bootstrap process remotely
	"""
	# Get the commandline arguments
	opts = get_opts()

	from bootstrapvz.common.tools import load_data
	# load the manifest data, we might want to modify it later on
	manifest_data = load_data(opts['MANIFEST'])

	# load the build servers file
	build_servers = load_data(opts['--servers'])
	# Pick a build server
	from build_servers import pick_build_server
	preferences = {}
	if opts['--name'] is not None:
		preferences['name'] = opts['--name']
	if opts['--release'] is not None:
		preferences['release'] = opts['--release']
	build_server = pick_build_server(build_servers, manifest_data, preferences)

	# Apply the build server settings to the manifest (e.g. the virtualbox guest additions path)
	manifest_data = build_server.apply_build_settings(manifest_data)

	# Load the manifest
	from bootstrapvz.base.manifest import Manifest
	manifest = Manifest(path=opts['MANIFEST'], data=manifest_data)

	# Set up logging
	from bootstrapvz.base.main import setup_loggers
	setup_loggers(opts)

	# Register deserialization handlers for objects
	# that will pass between server and client
	from . import register_deserialization_handlers
	register_deserialization_handlers()

	# Everything has been set up, connect to the server and begin the bootstrapping process
	run(manifest,
	    build_server,
	    debug=opts['--debug'],
	    dry_run=opts['--dry-run'])


def get_opts():
	"""Creates an argument parser and returns the arguments it has parsed
	"""
	from docopt import docopt
	usage = """bootstrap-vz-remote

Usage: bootstrap-vz-remote [options] --servers=<path> MANIFEST

Options:
  --servers <path>    Path to list of build servers
  --name <name>       Selects specific server from the build servers list
  --release <release> Require the build server OS to be a specific release
  --log <path>        Log to given directory [default: /var/log/bootstrap-vz]
                      If <path> is `-' file logging will be disabled.
  --pause-on-error    Pause on error, before rollback
  --dry-run           Don't actually run the tasks
  --color=auto|always|never
                     Colorize the console output [default: auto]
  --debug             Print debugging information
  -h, --help          show this help
	"""
	return docopt(usage)


def run(manifest, build_server, debug=False, dry_run=False):
	"""Connects to the remote build server, starts an RPC daemin
	on the other side and initiates a remote bootstrapping procedure
	"""
	bootstrap_info = None
	with build_server.connect() as (connection, callback_server):
		# Replace the standard SIGINT handler with a remote call to the server
		# so that it may abort the run.
		def abort(signum, frame):
			import logging
			logging.getLogger(__name__).warn('SIGINT received, asking remote to abort.')
			callback_server.abort_run()
		import signal
		orig_sigint = signal.signal(signal.SIGINT, abort)

		# Everything has been set up, begin the bootstrapping process
		bootstrap_info = connection.run(manifest,
		                                debug=debug,
		                                # We can't pause the bootstrapping process remotely, yet...
		                                pause_on_error=False,
		                                dry_run=dry_run)
		# Restore the old SIGINT handler
		signal.signal(signal.SIGINT, orig_sigint)
	return bootstrap_info
