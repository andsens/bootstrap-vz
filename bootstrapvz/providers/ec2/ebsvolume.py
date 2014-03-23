from base.fs.volume import Volume
from base.fs.exceptions import VolumeError
import time


class EBSVolume(Volume):

	def create(self, conn, zone):
		self.fsm.create(connection=conn, zone=zone)

	def _before_create(self, e):
		conn = e.connection
		zone = e.zone
		size = self.size.get_qty_in('GiB')
		self.volume = conn.create_volume(size, zone)
		while self.volume.volume_state() != 'available':
			time.sleep(5)
			self.volume.update()

	def attach(self, instance_id):
		self.fsm.attach(instance_id=instance_id)

	def _before_attach(self, e):
		instance_id = e.instance_id
		import os.path
		import string
		for letter in string.ascii_lowercase[5:]:
			dev_path = os.path.join('/dev', 'xvd' + letter)
			if not os.path.exists(dev_path):
				self.device_path = dev_path
				self.ec2_device_path = os.path.join('/dev', 'sd' + letter)
				break

		if self.device_path is None:
			raise VolumeError('Unable to find a free block device path for mounting the bootstrap volume')

		self.volume.attach(instance_id, self.ec2_device_path)
		while self.volume.attachment_state() != 'attached':
			time.sleep(2)
			self.volume.update()

	def _before_detach(self, e):
		self.volume.detach()
		while self.volume.attachment_state() is not None:
			time.sleep(2)
			self.volume.update()

	def _before_delete(self, e):
		self.volume.delete()

	def snapshot(self):
		snapshot = self.volume.create_snapshot()
		while snapshot.status != 'completed':
			time.sleep(2)
			snapshot.update()
		return snapshot
