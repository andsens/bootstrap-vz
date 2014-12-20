from __future__ import absolute_import
from . import Image
import virtualbox as vboxapi
import logging
log = logging.getLogger(__name__)


class VirtualBoxImage(Image):

	def __init__(self, manifest, image_path):
		super(VirtualBoxImage, self).__init__(manifest)
		self.image_path = image_path
		self.vbox = vboxapi.VirtualBox()

	def open(self):
		log.debug('Opening vbox medium `{path}\''.format(path=self.image_path))
		self.medium = self.vbox.open_medium(self.image_path,  # location
		                                    vboxapi.library.DeviceType.hard_disk,  # decive_type
		                                    vboxapi.library.AccessMode.read_only,  # access_mode
		                                    False)  # force_new_uuid

	def close(self):
		log.debug('Closing vbox medium `{path}\''.format(path=self.image_path))
		self.medium.close()

	def get_instance(self):
		import hashlib
		from ..instances.virtualbox import VirtualBoxInstance
		image_hash = hashlib.sha1(self.image_path).hexdigest()
		name = 'bootstrap-vz-{hash}'.format(hash=image_hash[:8])
		return VirtualBoxInstance(name, self)

	def __enter__(self):
		self.open()
		return self.get_instance()

	def __exit__(self, type, value, traceback):
		self.close()
