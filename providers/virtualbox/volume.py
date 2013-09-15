from common.fs.loopbackvolume import LoopbackVolume
from common.tools import log_check_call


class VirtualBoxVolume(LoopbackVolume):

	extension = 'vdi'

	def _create(self, e):
		self.image_path = e.image_path
		log_check_call(['/usr/bin/qemu-img', 'create', '-f', 'vdi', self.image_path, str(self.size) + 'M'])
