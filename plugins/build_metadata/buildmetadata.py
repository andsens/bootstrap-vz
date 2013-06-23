from base import Task
from common import phases


class PrintInfo(Task):
	description = 'Printing `info\' to the console'
	phase = phases.InstallOS

	def run(self, info):
		super(PrintInfo, self).run(info)
		print('info')
