"""This module holds functions and classes responsible for formatting the log output
both to a file and to the console.
.. module:: log
"""
import logging


def get_logfile_path(manifest_path):
	"""Returns the path to a logfile given a manifest
	The logfile name is constructed from the current timestamp and the basename of the manifest

	Args:
		manifest_path (str): The path to the manifest

	Returns:
		str. The path to the logfile
	"""
	import os.path
	from datetime import datetime

	manifest_basename = os.path.basename(manifest_path)
	manifest_name, _ = os.path.splitext(manifest_basename)
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	filename = "{timestamp}_{name}.log".format(timestamp=timestamp, name=manifest_name)
	return os.path.normpath(os.path.join(os.path.dirname(__file__), '../logs', filename))


def setup_logger(logfile=None, debug=False):
	"""Sets up the python logger to log to both a file and the console

	Args:
		logfile (str): Path to a logfile
		debug (bool): Whether to log debug output to the console
	"""
	root = logging.getLogger()
	# Make sure all logging statements are processed by our handlers, they decide the log level
	root.setLevel(logging.NOTSET)

	# Create a file log handler
	file_handler = logging.FileHandler(logfile)
	# Absolute timestamps are rather useless when bootstrapping, it's much more interesting
	# to see how long things take, so we log in a relative format instead
	file_handler.setFormatter(FileFormatter('[%(relativeCreated)s] %(levelname)s: %(message)s'))
	# The file log handler always logs everything
	file_handler.setLevel(logging.DEBUG)
	root.addHandler(file_handler)

	# Create a console log handler
	import sys
	console_handler = logging.StreamHandler(sys.stderr)
	# We want to colorize the output to the console, so we add a formatter
	console_handler.setFormatter(ConsoleFormatter())
	# Set the log level depending on the debug argument
	if debug:
		console_handler.setLevel(logging.DEBUG)
	else:
		console_handler.setLevel(logging.INFO)
	root.addHandler(console_handler)


class ConsoleFormatter(logging.Formatter):
	"""Formats log statements for the console
	"""
	level_colors = {logging.ERROR: 'red',
	                logging.WARNING: 'magenta',
	                logging.INFO: 'blue',
	                }

	def format(self, record):
		if(record.levelno in self.level_colors):
			# Colorize the message if we have a color for it (DEBUG has no color)
			from termcolor import colored
			record.msg = colored(record.msg, self.level_colors[record.levelno])
		return super(ConsoleFormatter, self).format(record)


class FileFormatter(logging.Formatter):
	"""Formats log statements for output to file
	Currently this is just a stub
	"""
	def format(self, record):
		return super(FileFormatter, self).format(record)
