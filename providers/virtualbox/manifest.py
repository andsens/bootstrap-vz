import base


class Manifest(base.Manifest):
	def validate(self, data):
		super(Manifest, self).validate(data)
		from os import path
		schema_path = path.join(path.dirname(__file__), 'manifest-schema.json')
		self.schema_validate(data, schema_path)

	def parse(self, data):
		super(Manifest, self).parse(data)
		self.virtualization = None
		self.image          = data['image']
