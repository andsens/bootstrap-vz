from base import Task
from common import phases
from plugins.packages import tasks as packages


class ImageExecuteCommand(Task):
	description = 'Execute command in the image'
	phase = phases.system_modification
	predecessors = [packages.AddUserPackages, packages.AddLocalUserPackages]

	def run(self, info):
		from common.tools import log_check_call

		for user_cmd in info.manifest.plugins['image_commands']['commands']:
			command = []
			for elt in user_cmd:
				fragment = elt.format(root=info.root)
				command.append(fragment)
			log_check_call(command)
