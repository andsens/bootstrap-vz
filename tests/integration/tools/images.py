

class Image(object):

	def __init__(self, manifest):
		self.manifest = manifest

	def destroy(self):
		pass


class VirtualBoxImage(Image):

	def __init__(self, manifest, image_path):
		super(VirtualBoxImage, self).__init__(manifest)
		self.image_path = image_path
		self.medium = self.vbox.open_medium(location=self.image.image_path,
		                                    decive_type=self.vbox.library.DeviceType.HardDisk,
		                                    access_mode=self.vbox.library.AccessMode.read_only,
		                                    force_new_uuid=False)

	def destroy(self):
		self.medium.delete_storage()
		import os
		os.remove(self.image_path)
