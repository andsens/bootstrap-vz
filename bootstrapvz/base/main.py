"""Main module containing all the setup necessary for running the bootstrapping process
"""

import logging
log = logging.getLogger(__name__)


def main():
	"""Main function for invoking the bootstrap process

	:raises Exception: When the invoking user is not root and --dry-run isn't specified
	"""
	# Get the commandline arguments
	opts = get_opts()
	# Require root privileges, except when doing a dry-run where they aren't needed
	import os
	if os.geteuid() != 0 and not opts['--dry-run']:
		raise Exception('This program requires root privileges.')

	# Set up logging
	setup_loggers(opts)

	# Load the manifest
	from manifest import Manifest
	manifest = Manifest(path=opts['MANIFEST'])

	# Everything has been set up, begin the bootstrapping process
	run(manifest,
	    debug=opts['--debug'],
	    pause_on_error=opts['--pause-on-error'],
	    dry_run=opts['--dry-run'])


def get_opts():
	"""Creates an argument parser and returns the arguments it has parsed
	"""
	from docopt import docopt
	usage = """bootstrap-vz

Usage: bootstrap-vz [options] MANIFEST

Options:
  --log <path>       Log to given directory [default: /var/log/bootstrap-vz]
                     If <path> is `-' file logging will be disabled.
  --pause-on-error   Pause on error, before rollback
  --dry-run          Don't actually run the tasks
  --debug            Print debugging information
  -h, --help         show this help
	"""
	return docopt(usage)


def setup_loggers(opts):
	"""Sets up the file and console loggers

	:params dict opts: Dictionary of options from the commandline
	"""
	import logging
	root = logging.getLogger()
	root.setLevel(logging.NOTSET)

	import log
	# Log to file unless --log is a single dash
	if opts['--log'] != '-':
		import os.path
		log_filename = log.get_log_filename(opts['MANIFEST'])
		logpath = os.path.join(opts['--log'], log_filename)
		file_handler = log.get_file_handler(path=logpath, debug=True)
		root.addHandler(file_handler)

	console_handler = log.get_console_handler(debug=opts['--debug'])
	root.addHandler(console_handler)


def run(manifest, debug=False, pause_on_error=False, dry_run=False):
	"""Runs the bootstrapping process

	:params Manifest manifest: The manifest to run the bootstrapping process for
	:params bool debug: Whether to turn debugging mode on
	:params bool pause_on_error: Whether to pause on error, before rollback
	:params bool dry_run: Don't actually run the tasks
	"""
	# Get the tasklist
	from tasklist import load_tasks
	from tasklist import TaskList
	tasks = load_tasks('resolve_tasks', manifest)
	tasklist = TaskList(tasks)
	# 'resolve_tasks' is the name of the function to call on the provider and plugins

	# Create the bootstrap information object that'll be used throughout the bootstrapping process
	from bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest=manifest, debug=debug)

	try:
		# Run all the tasks the tasklist has gathered
		tasklist.run(info=bootstrap_info, dry_run=dry_run)
		# We're done! :-)
		log.info('Successfully completed bootstrapping')
	except (Exception, KeyboardInterrupt) as e:
		# When an error occurs, log it and begin rollback
		log.exception(e)
		if pause_on_error:
			# The --pause-on-error is useful when the user wants to inspect the volume before rollback
			raw_input('Press Enter to commence rollback')
		log.error('Rolling back')

		# Create a useful little function for the provider and plugins to use,
		# when figuring out what tasks should be added to the rollback list.
		def counter_task(taskset, task, counter):
			"""counter_task() adds the second argument to the rollback tasklist
			if the first argument is present in the list of completed tasks

			:param set taskset: The taskset to add the rollback task to
			:param Task task: The task to look for in the completed tasks list
			:param Task counter: The task to add to the rollback tasklist
			"""
			if task in tasklist.tasks_completed and counter not in tasklist.tasks_completed:
				taskset.add(counter)

		# Ask the provider and plugins for tasks they'd like to add to the rollback tasklist
		# Any additional arguments beyond the first two are passed directly to the provider and plugins
		rollback_tasks = load_tasks('resolve_rollback_tasks', manifest, tasklist.tasks_completed, counter_task)
		rollback_tasklist = TaskList(rollback_tasks)

		# Run the rollback tasklist
		rollback_tasklist.run(info=bootstrap_info, dry_run=dry_run)
		log.info('Successfully completed rollback')
		raise e
	return bootstrap_info
