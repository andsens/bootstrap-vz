from base import Task


class AddSudoPackage(Task):
	description = 'Adding ``sudo\'\' to the image packages'

	def run(self, info):
		super(AddSudoPackage, self).run(info)
		info.img_packages[0].add('sudo')
