from base import Task


class PrintInfo(Task):
	def run(self, info):
		super(PrintInfo, self).run(info)
		print('info')
