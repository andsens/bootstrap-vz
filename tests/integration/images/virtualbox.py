from __future__ import absolute_import
from . import Image
import virtualbox as vboxapi


class VirtualBoxImage(Image):

	def __init__(self, manifest, image_path):
		super(VirtualBoxImage, self).__init__(manifest)
		self.image_path = image_path
		self.vbox = vboxapi.VirtualBox()
		self.medium = self.vbox.open_medium(self.image_path,  # location
		                                    vboxapi.library.DeviceType.hard_disk,  # decive_type
		                                    vboxapi.library.AccessMode.read_only,  # access_mode
		                                    False)  # force_new_uuid

	def destroy(self):
		self.medium.close()
