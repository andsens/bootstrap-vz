import base


class Manifest(base.Manifest):
	def validate(self, data):
		from os import path
		schema_path = path.normpath(path.join(path.dirname(__file__), 'manifest-schema.json'))
		super(Manifest, self).validate(data, schema_path)

	def parse(self, data):
		super(Manifest, self).parse(data)
		self.credentials    = data['credentials']
		self.virtualization = data['virtualization']
