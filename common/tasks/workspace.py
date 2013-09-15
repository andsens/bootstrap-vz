from base import Task
from common import phases


class CreateWorkspace(Task):
	description = 'Creating workspace'
	phase = phases.preparation

	def run(self, info):
		import os
		os.makedirs(info.workspace)


class DeleteWorkspace(Task):
	description = 'Deleting workspace'
	phase = phases.cleaning

	def run(self, info):
		import os
		os.rmdir(info.workspace)
