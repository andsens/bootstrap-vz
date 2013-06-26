from base import Task
from common import phases
from providers.ec2.tasks.host import GetInfo


class PrintInfo(Task):
	description = 'Printing `info\' to the console'
	phase = phases.install_os
	after = [GetInfo]

	def run(self, info):
		print('info')
