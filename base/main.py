import logging


def main():
	args = get_args()
	setup_logger(args)
	run(args)


def get_args():
	from argparse import ArgumentParser
	parser = ArgumentParser(description='Bootstrap Debian for the cloud.')
	parser.add_argument('--debug', action='store_true',
	                    help='Print debugging information')
	parser.add_argument('manifest', help='Manifest file to use for bootstrapping', metavar='MANIFEST')
	return parser.parse_args()


def setup_logger(args):
	import sys
	import os.path
	from datetime import datetime
	root = logging.getLogger()
	root.setLevel(logging.NOTSET)

	manifest_basename = os.path.basename(args.manifest)
	manifest_name, _ = os.path.splitext(manifest_basename)
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	filename = "{timestamp}_{name}.log".format(timestamp=timestamp, name=manifest_name)
	path=os.path.normpath(os.path.join(os.path.dirname(__file__), '../logs', filename))
	file_handler = logging.FileHandler(path)
	file_handler.setFormatter(FileFormatter('[%(asctime)s] %(message)s'))
	file_handler.setLevel(logging.DEBUG)
	root.addHandler(file_handler)

	console_handler = logging.StreamHandler(sys.stderr)
	console_handler.setFormatter(ConsoleFormatter())
	if args.debug:
		console_handler.setLevel(logging.DEBUG)
	else:
		console_handler.setLevel(logging.INFO)
	root.addHandler(console_handler)


def run(args):
	from manifest import load_manifest
	(provider, manifest) = load_manifest(args.manifest)

	from tasklist import TaskList
	tasklist = TaskList()
	provider.modify_tasklist(tasklist, manifest)
	tasklist.plugins(manifest)

	from bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest=manifest, debug=args.debug)
	tasklist.run(bootstrap_info)


class ConsoleFormatter(logging.Formatter):

	def format(self, record):
		from task import Task
		if(isinstance(record.msg, Task)):
			task = record.msg
			if(task.description is not None):
				return '\033[0;34m{description}\033[0m'.format(description=task.description)
			else:
				return '\033[0;34mRunning {task}\033[0m'.format(task=task)
		return super(ConsoleFormatter, self).format(record)


class FileFormatter(logging.Formatter):

	def format(self, record):
		from task import Task
		from datetime import datetime
		if(isinstance(record.msg, Task)):
			task = record.msg
			if(task.description is not None):
				record.msg = '{description} (running {task})'.format(task=task, description=task.description)
			else:
				record.msg = 'Running {task}'.format(task=task)
			message = super(FileFormatter, self).format(record)
			record.msg = task
		else:
			message = super(FileFormatter, self).format(record)
		return message
