import common


class Manifest(common.Manifest):
	def parse(self, data):
		super(Manifest, self).parse(data)
		self.credentials = data["credentials"]
		self.virtualization = data["virtualization"]

	def validate(self):
		super(Manifest, self).validate()
