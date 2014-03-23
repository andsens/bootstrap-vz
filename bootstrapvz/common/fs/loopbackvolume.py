from base.fs.volume import Volume
from common.tools import log_check_call


class LoopbackVolume(Volume):

	extension = 'raw'

	def create(self, image_path):
		self.fsm.create(image_path=image_path)

	def _before_create(self, e):
		self.image_path = e.image_path
		vol_size = str(self.size.get_qty_in('MiB')) + 'M'
		log_check_call(['qemu-img', 'create', '-f', 'raw', self.image_path, vol_size])

	def _before_attach(self, e):
		[self.loop_device_path] = log_check_call(['losetup', '--show', '--find', self.image_path])
		self.device_path = self.loop_device_path

	def _before_detach(self, e):
		log_check_call(['losetup', '--detach', self.loop_device_path])
		del self.loop_device_path
		del self.device_path

	def _before_delete(self, e):
		from os import remove
		remove(self.image_path)
		del self.image_path
