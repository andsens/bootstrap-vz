from base import Task
from common import phases
from common.tasks import volume


class Create(Task):
	description = 'Creating the EBS volume'
	phase = phases.volume_creation
	before = [volume.Attach]

	def run(self, info):
		info.volume.create(info.connection, info.host['availabilityZone'])


class Snapshot(Task):
	description = 'Creating a snapshot of the EBS volume'
	phase = phases.image_registration

	def run(self, info):
		info.snapshot = info.volume.snapshot()
