__all__ = ['Phase', 'Task', 'main']
from phase import Phase
from task import Task
from main import main


def validate_manifest(data, validator, error):
	"""Validates the manifest using the base manifest

	:param dict data: The data of the manifest
	:param function validator: The function that validates the manifest given the data and a path
	:param function error: The function tha raises an error when the validation fails
	"""
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)

	# Check the bootloader/partitioning configuration.
	# Doing this via the schema is a pain and does not output a useful error message.
	if data['system']['bootloader'] == 'grub' and data['volume']['partitions']['type'] == 'none':
			error('Grub cannot boot from unpartitioned disks', ['system', 'bootloader'])
