from qemuvolume import QEMUVolume


class VirtualDiskImage(QEMUVolume):

	extension = 'vdi'
	qemu_format = 'vdi'
	ovf_uri = None

	def get_uuid(self):
		import uuid
		with open(self.image_path) as image:
			image.seek(392)
			return uuid.UUID(bytes_le=image.read(16))
