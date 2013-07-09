from base import Task
from common import phases
from common.exceptions import TaskError
from filesystem import UnmountVolume
import time


class CreateVolume(Task):
	description = 'Creating an EBS volume for bootstrapping'
	phase = phases.volume_creation

	def run(self, info):
		volume_size = int(info.manifest.volume['size']/1024)

		info.volume = info.connection.create_volume(volume_size, info.host['availabilityZone'])
		while info.volume.volume_state() != 'available':
			time.sleep(5)
			info.volume.update()


class AttachVolume(Task):
	description = 'Attaching the EBS volume'
	phase = phases.volume_creation
	after = [CreateVolume]

	def run(self, info):
		def char_range(c1, c2):
			"""Generates the characters from `c1` to `c2`, inclusive."""
			for c in xrange(ord(c1), ord(c2)+1):
				yield chr(c)

		import os.path
		info.bootstrap_device = {}
		for letter in char_range('f', 'z'):
			dev_path = os.path.join('/dev', 'xvd' + letter)
			if not os.path.exists(dev_path):
				info.bootstrap_device['path'] = dev_path
				info.bootstrap_device['ec2_path'] = os.path.join('/dev', 'sd' + letter)
				break
		if 'path' not in info.bootstrap_device:
			raise VolumeError('Unable to find a free block device path for mounting the bootstrap volume')

		info.volume.attach(info.host['instanceId'], info.bootstrap_device['ec2_path'])
		while info.volume.attachment_state() != 'attached':
			time.sleep(2)
			info.volume.update()


class DetachVolume(Task):
	description = 'Detaching the EBS volume'
	phase = phases.volume_unmounting
	after = [UnmountVolume]

	def run(self, info):
		info.volume.detach()
		while info.volume.attachment_state() is not None:
			time.sleep(2)
			info.volume.update()


class CreateSnapshot(Task):
	description = 'Creating a snapshot of the EBS volume'
	phase = phases.image_registration

	def run(self, info):
		info.snapshot = info.volume.create_snapshot()
		while info.snapshot.status != 'completed':
			time.sleep(2)
			info.snapshot.update()


class DeleteVolume(Task):
	description = 'Deleting the EBS volume'
	phase = phases.cleaning
	after = []

	def run(self, info):
		info.volume.delete()
		del info.volume


class VolumeError(TaskError):
	pass
