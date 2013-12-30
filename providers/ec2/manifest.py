import base
from common.exceptions import ManifestError


class Manifest(base.Manifest):
	def validate(self, data):
		super(Manifest, self).validate(data)
		from os import path
		self.schema_validate(data, path.join(path.dirname(__file__), 'manifest-schema.json'))
		if data['volume']['backing'] == 'ebs':
			volume_size = self._calculate_volume_size(data['volume']['partitions'])
			if volume_size % 1024 != 0:
				msg = ('The volume size must be a multiple of 1024 when using EBS backing '
				       '(MBR partitioned volumes are 1MB larger than specified, for the post-mbr gap)')
				raise ManifestError(msg, self)
		else:
			self.schema_validate(data, path.join(path.dirname(__file__), 'manifest-schema-s3.json'))

		if data['virtualization'] == 'pvm' and data['system']['bootloader'] != 'pvgrub':
			raise ManifestError('Paravirtualized AMIs only support pvgrub as a bootloader', self)
		if data['virtualization'] == 'hvm' and data['system']['bootloader'] != 'extlinux':
			raise ManifestError('HVM AMIs only support extlinux as a bootloader', self)

	def parse(self, data):
		super(Manifest, self).parse(data)
		self.credentials    = data['credentials']
		self.virtualization = data['virtualization']
		self.image          = data['image']

	def _calculate_volume_size(self, partitions):
		if partitions['type'] == 'mbr':
			size = 1
		else:
			size = 0
		if 'boot' in partitions:
			size += partitions['boot']['size']
		size += partitions['root']['size']
		if 'swap' in partitions:
			size += partitions['swap']['size']
		return size
