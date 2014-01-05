import logging
log = logging.getLogger(__name__)


def main():
	import log
	args = get_args()
	logfile = log.get_logfile_path(args.manifest)
	log.setup_logger(logfile=logfile, debug=args.debug)
	run(args)


def get_args():
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
	from manifest import Manifest
	manifest = Manifest(args.manifest)

	from tasklist import TaskList
	tasklist = TaskList()
	tasklist.load('resolve_tasks', manifest)

	from bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest=manifest, debug=args.debug)

	try:
		tasklist.run(info=bootstrap_info, dry_run=args.dry_run)
		log.info('Successfully completed bootstrapping')
	except (Exception, KeyboardInterrupt) as e:
		log.exception(e)
		if args.pause_on_error:
			raw_input("Press Enter to commence rollback")
		log.error('Rolling back')

		rollback_tasklist = TaskList()

		def counter_task(task, counter):
			if task in tasklist.tasks_completed and counter not in tasklist.tasks_completed:
				rollback_tasklist.tasks.add(counter)
		rollback_tasklist.load('resolve_rollback_tasks', manifest, counter_task)

		rollback_tasklist.run(info=bootstrap_info, dry_run=args.dry_run)
		log.info('Successfully completed rollback')
