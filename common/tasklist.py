

class TaskList(list):
	def run(self, info):
		for task in self:
			task.run(info)

	def before(self, task):
		pass

	def replace(self, task):
		pass

	def after(self, task):
		pass
