import logging


def get_logfile_path(manifest_path):
	import sys
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
	file_handler.setFormatter(FileFormatter('[%(asctime)s] %(message)s'))
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
