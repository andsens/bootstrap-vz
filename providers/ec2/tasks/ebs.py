from base import Task
from common import phases
from common.exceptions import TaskException
from connection import Connect

class CreateVolume(Task):
	description = 'Creating an EBS volume for bootstrapping'
	phase = phases.volume_creation
	after = [Connect]

	def run(self, info):
		volume_size = int(info.manifest.volume['size']/1024)
		info.volume = info.conn.create_volume(volume_size, info.host['availabilityZone'])

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
		import os.stat
		from stat import S_ISBLK
		for letter in char_range('a', 'z'):
			dev_path = os.path.join('/dev', 'xvd' + letter)
			mode = os.stat(dev_path).st_mode
			if S_ISBLK(mode):
				info.bootstrap_device = {'path': dev_path}
				break
		if 'path' not in info.bootstrap_device:
			raise VolumeError('Unable to find a free block device path for mounting the bootstrap volume')
		info.conn.volume.attach(info.host['instanceId'], info.bootstrap_device['path'])

class VolumeError(TaskException):
	pass
