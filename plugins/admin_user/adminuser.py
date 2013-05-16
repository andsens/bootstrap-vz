from common import Task


class AddSudoPackage(Task):
	def run(self, info):
		super(AddSudoPackage, self).run(info)
		info.img_packages[0].add('sudo')
