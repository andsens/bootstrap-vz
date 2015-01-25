from image import Image
import virtualbox
import logging
from contextlib import contextmanager
log = logging.getLogger(__name__)


def initialize_image(manifest, build_server, bootstrap_info):
	from bootstrapvz.remote.build_servers import LocalBuildServer
	if isinstance(build_server, LocalBuildServer):
		image_path = bootstrap_info.volume.image_path
	else:
		import tempfile
		handle, image_path = tempfile.mkstemp()
		import os
		os.close(handle)
		try:
			build_server.download(bootstrap_info.volume.image_path, image_path)
		except (Exception, KeyboardInterrupt):
			os.remove(image_path)
			raise
		finally:
			build_server.delete(bootstrap_info.volume.image_path)
	image = VirtualBoxImage(manifest, image_path)
	return image


class VirtualBoxImage(Image):

	def __init__(self, manifest, image_path):
		super(VirtualBoxImage, self).__init__(manifest)
		self.image_path = image_path
		self.vbox = virtualbox.VirtualBox()

	def open(self):
		log.debug('Opening vbox medium `{path}\''.format(path=self.image_path))
		self.medium = self.vbox.open_medium(self.image_path,  # location
		                                    virtualbox.library.DeviceType.hard_disk,  # device_type
		                                    virtualbox.library.AccessMode.read_only,  # access_mode
		                                    False)  # force_new_uuid

	def close(self):
		log.debug('Closing vbox medium `{path}\''.format(path=self.image_path))
		self.medium.close()

	def destroy(self):
		log.debug('Deleting vbox image `{path}\''.format(path=self.image_path))
		import os
		os.remove(self.image_path)
		del self.image_path

	@contextmanager
	def get_instance(self):
		import hashlib
		image_hash = hashlib.sha1(self.image_path).hexdigest()
		name = 'bootstrap-vz-{hash}'.format(hash=image_hash[:8])

		self.open()
		try:
			from ..instances.vbox import boot_image
			with boot_image(name, self) as instance:
				yield instance
		finally:
			self.close()
