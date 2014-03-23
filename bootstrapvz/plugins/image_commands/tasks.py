from base import Task
from common import phases


class ImageExecuteCommand(Task):
	description = 'Execute command in the image'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from common.tools import log_check_call
		for raw_command in info.manifest.plugins['image_commands']['commands']:
			command = map(lambda part: part.format(root=info.root, **info.manifest_vars), raw_command)
			log_check_call(command)
