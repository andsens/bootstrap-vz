import base


class Manifest(base.Manifest):
	def validate(self, data):
		super(Manifest, self).validate(data)
		from os import path
		schema_path = path.join(path.dirname(__file__), 'manifest-schema.json')
		self.schema_validate(data, schema_path)

	def parse(self, data):
		super(Manifest, self).parse(data)
		self.credentials    = data['credentials']
		self.virtualization = data['virtualization']
		self.image          = data['image']
		if 'loopback_dir' not in self.volume and self.volume['backing'].lower() == 's3':
			self.volume['loopback_dir'] = '/tmp'
