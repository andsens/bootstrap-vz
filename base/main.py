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
	parser.add_argument('manifest', help='Manifest file to use for bootstrapping', metavar='MANIFEST')
	return parser.parse_args()


def run(args):
	from manifest import load_manifest
	(provider, manifest) = load_manifest(args.manifest)

	from tasklist import TaskList
	tasklist = TaskList()
	provider.tasks(tasklist, manifest)
	for plugin in manifest.loaded_plugins:
		plugin.tasks(tasklist, manifest)

	from bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest=manifest, debug=args.debug)

	try:
		tasklist.run(bootstrap_info)
		log.info('Successfully completed bootstrapping')
	except (Exception, KeyboardInterrupt) as e:
		log.exception(e)
		log.error('Rolling back')
		rollback_tasklist = TaskList()
		provider.rollback_tasks(rollback_tasklist, tasklist.tasks_completed, manifest)
		for plugin in manifest.loaded_plugins:
			rollback_tasks = getattr(plugin, 'rollback_tasks', None)
			if callable(rollback_tasks):
				plugin.rollback_tasks(rollback_tasklist, tasklist.tasks_completed, manifest)
		rollback_tasklist.run(bootstrap_info)
		log.info('Successfully completed rollback')
