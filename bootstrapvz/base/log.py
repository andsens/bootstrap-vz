"""This module holds functions and classes responsible for formatting the log output
both to a file and to the console.
"""
import logging


def get_console_handler(debug, colorize):
	"""Returns a log handler for the console
	The handler color codes the different log levels

	:params bool debug: Whether to set the log level to DEBUG (otherwise INFO)
	:params bool colorize: Whether to colorize console output
	:return: The console logging handler
	"""
	# Create a console log handler
	import sys
	console_handler = logging.StreamHandler(sys.stderr)
	if colorize:
		# We want to colorize the output to the console, so we add a formatter
		console_handler.setFormatter(ConsoleFormatter())
	# Set the log level depending on the debug argument
	if debug:
		console_handler.setLevel(logging.DEBUG)
	else:
		console_handler.setLevel(logging.INFO)
	return console_handler


def get_file_handler(path, debug):
	"""Returns a log handler for the given path
	If the parent directory of the logpath does not exist it will be created
	The handler outputs relative timestamps (to when it was created)

	:params str path: The full path to the logfile
	:params bool debug: Whether to set the log level to DEBUG (otherwise INFO)
	:return: The file logging handler
	"""
	import os.path
	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))
	# Create the log handler
	file_handler = logging.FileHandler(path)
	# Absolute timestamps are rather useless when bootstrapping, it's much more interesting
	# to see how long things take, so we log in a relative format instead
	file_handler.setFormatter(FileFormatter('[%(relativeCreated)s] %(levelname)s: %(message)s'))
	# The file log handler always logs everything
	file_handler.setLevel(logging.DEBUG)
	return file_handler


def get_log_filename(manifest_path):
	"""Returns the path to a logfile given a manifest
	The logfile name is constructed from the current timestamp and the basename of the manifest

	:param str manifest_path: The path to the manifest
	:return: The path to the logfile
	:rtype: str
	"""
	import os.path
	from datetime import datetime

	manifest_basename = os.path.basename(manifest_path)
	manifest_name, _ = os.path.splitext(manifest_basename)
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	filename = '{timestamp}_{name}.log'.format(timestamp=timestamp, name=manifest_name)
	return filename


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
