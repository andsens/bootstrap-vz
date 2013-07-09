import base
from common.exceptions import ManifestError


class Manifest(base.Manifest):
	def validate(self, data):
		super(Manifest, self).validate(data)
		from os import path
		schema_path = path.join(path.dirname(__file__), 'manifest-schema.json')
		self.schema_validate(data, schema_path)
		if data['volume']['backing'] == 'ebs' and data['volume']['size'] % 1024 != 0:
			msg = 'The volume size must be a multiple of 1024 when using EBS backing'
			raise ManifestError(msg, self)

	def parse(self, data):
		super(Manifest, self).parse(data)
		self.credentials    = data['credentials']
		self.virtualization = data['virtualization']
		self.image          = data['image']
		if data['volume']['backing'] == 'ebs':
			self.ebs_volume_size = data['volume']['size'] / 1024
