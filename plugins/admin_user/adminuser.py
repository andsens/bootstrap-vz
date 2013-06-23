from base import Task
from common import phases
from providers.ec2.tasks.packages import ImagePackages
from providers.ec2.tasks.host import CheckPackages


class AddSudoPackage(Task):
	description = 'Adding ``sudo\'\' to the image packages'
	phase = phases.Preparation
	after = [ImagePackages]
	before = [CheckPackages]

	def run(self, info):
		super(AddSudoPackage, self).run(info)
		info.img_packages[0].add('sudo')
