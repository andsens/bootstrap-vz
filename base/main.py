"""Main module containing all the setup necessary for running the bootstrapping process
.. module:: main
"""

import logging
log = logging.getLogger(__name__)


def main():
	"""Main function for invoking the bootstrap process

	Raises:
		Exception
	"""
	# Get the commandline arguments
	import os
	args = get_args()
	# Require root privileges, except when doing a dry-run where they aren't needed
	if os.geteuid() != 0 and not args.dry_run:
		raise Exception('This program requires root privileges.')
	# Setup logging
	import log
	logfile = log.get_logfile_path(args.manifest)
	log.setup_logger(logfile=logfile, debug=args.debug)
	# Everything has been set up, begin the bootstrapping process
	run(args)


def get_args():
	"""Creates an argument parser and returns the arguments it has parsed
	"""
	from argparse import ArgumentParser
	parser = ArgumentParser(description='Bootstrap Debian for the cloud.')
	parser.add_argument('--debug', action='store_true',
	                    help='Print debugging information')
	parser.add_argument('--pause-on-error', action='store_true',
	                    help='Pause on error, before rollback')
	parser.add_argument('--dry-run', action='store_true',
	                    help='Dont\'t actually run the tasks')
	parser.add_argument('manifest', help='Manifest file to use for bootstrapping', metavar='MANIFEST')
	return parser.parse_args()


def run(args):
	"""Runs the bootstrapping process

	Args:
		args (dict): Dictionary of arguments from the commandline
	"""
	# Load the manifest
	from manifest import Manifest
	manifest = Manifest(args.manifest)

	# Get the tasklist
	from tasklist import TaskList
	tasklist = TaskList()
	# 'resolve_tasks' is the name of the function to call on the provider and plugins
	tasklist.load('resolve_tasks', manifest)

	# Create the bootstrap information object that'll be used throughout the bootstrapping process
	from bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest=manifest, debug=args.debug)

	try:
		# Run all the tasks the tasklist has gathered
		tasklist.run(info=bootstrap_info, dry_run=args.dry_run)
		# We're done! :-)
		log.info('Successfully completed bootstrapping')
	except (Exception, KeyboardInterrupt) as e:
		# When an error occurs, log it and begin rollback
		log.exception(e)
		if args.pause_on_error:
			# The --pause-on-error is useful when the user wants to inspect the volume before rollback
			raw_input('Press Enter to commence rollback')
		log.error('Rolling back')

		# Create a new tasklist to gather the necessary tasks for rollback
		rollback_tasklist = TaskList()

		# Create a useful little function for the provider and plugins to use,
		# when figuring out what tasks should be added to the rollback list.
		def counter_task(task, counter):
			"""counter_task() adds the second argument to the rollback tasklist
			if the first argument is present in the list of completed tasks

			Args:
				task (Task): The task to look for in the completed tasks list
				counter (Task): The task to add to the rollback tasklist
			"""
			if task in tasklist.tasks_completed and counter not in tasklist.tasks_completed:
				rollback_tasklist.tasks.add(counter)
		# Ask the provider and plugins for tasks they'd like to add to the rollback tasklist
		# Any additional arguments beyond the first two are passed directly to the provider and plugins
		rollback_tasklist.load('resolve_rollback_tasks', manifest, counter_task)

		# Run the rollback tasklist
		rollback_tasklist.run(info=bootstrap_info, dry_run=args.dry_run)
		log.info('Successfully completed rollback')
