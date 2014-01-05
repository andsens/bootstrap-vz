__all__ = ['Phase', 'Task', 'main']
from phase import Phase
from task import Task
from main import main


def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.json'))
	validator(data, schema_path)
