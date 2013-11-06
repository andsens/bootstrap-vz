from base import Task
from common import phases
from common.tasks import workspace


class Attach(Task):
	description = 'Attaching the volume'
	phase = phases.volume_creation

	def run(self, info):
		info.volume.attach()


class Detach(Task):
	description = 'Detaching the volume'
	phase = phases.volume_unmounting

	def run(self, info):
		info.volume.detach()


class Delete(Task):
	description = 'Deleting the volume'
	phase = phases.cleaning
	before = [workspace.DeleteWorkspace]

	def run(self, info):
		info.volume.delete()
