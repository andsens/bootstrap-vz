from base import Task


class PrintInfo(Task):
	description = 'Printing `info\' to the console'

	def run(self, info):
		super(PrintInfo, self).run(info)
		print('info')
