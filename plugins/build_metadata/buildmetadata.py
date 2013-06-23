from base import Task
from common import phases
from providers.ec2.tasks.host import GetInfo


class PrintInfo(Task):
	description = 'Printing `info\' to the console'
	phase = phases.InstallOS
	after = [GetInfo]

	def run(self, info):
		super(PrintInfo, self).run(info)
		print('info')
