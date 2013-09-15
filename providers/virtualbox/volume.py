from common.fs.loopbackvolume import LoopbackVolume
from common.tools import log_check_call


class VirtualBoxVolume(LoopbackVolume):

	def create(self, image_path):
		super(VirtualBoxVolume, self).create(self)
		self.image_path = image_path
		log_check_call(['/usr/bin/qemu-img', 'create', '-f', 'vdi', self.image_path, str(self.size) + 'M'])
		self.created = True
