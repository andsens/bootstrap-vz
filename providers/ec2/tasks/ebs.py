from base import Task
from common import phases


class Create(Task):
	description = 'Creating the EBS volume'
	phase = phases.volume_creation

	def run(self, info):
		info.volume.create(info.connection, info.host['availabilityZone'])


class Attach(Task):
	description = 'Attaching the volume'
	phase = phases.volume_creation
	after = [Create]

	def run(self, info):
		info.volume.attach(info.host['instanceId'])


class Snapshot(Task):
	description = 'Creating a snapshot of the EBS volume'
	phase = phases.image_registration

	def run(self, info):
		info.snapshot = info.volume.snapshot()
