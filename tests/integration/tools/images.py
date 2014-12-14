import virtualbox


class Image(object):

	def __init__(self, manifest):
		self.manifest = manifest

	def destroy(self):
		pass


class VirtualBoxImage(Image):

	def __init__(self, manifest, image_path):
		super(VirtualBoxImage, self).__init__(manifest)
		self.image_path = image_path
		self.vbox = virtualbox.VirtualBox()
		self.medium = self.vbox.open_medium(self.image_path,  # location
		                                    virtualbox.library.DeviceType.hard_disk,  # decive_type
		                                    virtualbox.library.AccessMode.read_only,  # access_mode
		                                    False)  # force_new_uuid

	def destroy(self):
		self.medium.close()
