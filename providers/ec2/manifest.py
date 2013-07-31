import base
from common.exceptions import ManifestError


class Manifest(base.Manifest):
	def validate(self, data):
		super(Manifest, self).validate(data)
		from os import path
		schema_path = path.join(path.dirname(__file__), 'manifest-schema.json')
		self.schema_validate(data, schema_path)
		if data['volume']['backing'] == 'ebs':
			if data['volume']['size'] % 1024 != 0:
				msg = 'The volume size must be a multiple of 1024 when using EBS backing'
				raise ManifestError(msg, self)
		else:
			schema_path = path.join(path.dirname(__file__), 'manifest-schema-s3.json')
			self.schema_validate(data, schema_path)

	def parse(self, data):
		super(Manifest, self).parse(data)
		self.credentials    = data['credentials']
		self.virtualization = data['virtualization']
		self.image          = data['image']
		if data['volume']['backing'] == 'ebs':
			self.ebs_volume_size = data['volume']['size'] / 1024
		if 'loopback_dir' not in self.volume and self.volume['backing'].lower() == 's3':
			self.volume['loopback_dir'] = '/tmp'
		if 'bundle_dir' not in self.image and self.volume['backing'].lower() == 's3':
			self.image['bundle_dir'] = '/tmp'
