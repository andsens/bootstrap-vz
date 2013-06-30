import logging


def get_logfile_path(manifest_path):
	import os.path
	from datetime import datetime

	manifest_basename = os.path.basename(manifest_path)
	manifest_name, _ = os.path.splitext(manifest_basename)
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	filename = "{timestamp}_{name}.log".format(timestamp=timestamp, name=manifest_name)
	return os.path.normpath(os.path.join(os.path.dirname(__file__), '../logs', filename))


def setup_logger(logfile=None, debug=False):
	root = logging.getLogger()
	root.setLevel(logging.NOTSET)

	file_handler = logging.FileHandler(logfile)
	file_handler.setFormatter(FileFormatter('[%(relativeCreated)s] %(levelname)s: %(message)s'))
	file_handler.setLevel(logging.DEBUG)
	root.addHandler(file_handler)

	import sys
	console_handler = logging.StreamHandler(sys.stderr)
	console_handler.setFormatter(ConsoleFormatter())
	if debug:
		console_handler.setLevel(logging.DEBUG)
	else:
		console_handler.setLevel(logging.INFO)
	root.addHandler(console_handler)


class ConsoleFormatter(logging.Formatter):
	level_colors = {logging.ERROR: 'red',
	                logging.WARNING: 'magenta',
	                logging.INFO: 'blue',
	                }

	def format(self, record):
		if(record.levelno in self.level_colors):
			from termcolor import colored
			record.msg = colored(record.msg, self.level_colors[record.levelno])
		return super(ConsoleFormatter, self).format(record)


class FileFormatter(logging.Formatter):
	def format(self, record):
		return super(FileFormatter, self).format(record)
