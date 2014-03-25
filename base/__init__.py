__all__ = ['Phase', 'Task', 'main']
from phase import Phase
from task import Task
from main import main


def validate_manifest(data, validator, error):
	"""Validates the manifest using the base manifest

	Args:
		data (dict): The data of the manifest
		validator (function): The function that validates the manifest given the data and a path
		error (function): The function tha raises an error when the validation fails
	"""
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)
