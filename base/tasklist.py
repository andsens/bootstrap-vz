

class TaskList(list):

	def plugins(self, manifest):
		for plugin in manifest.loaded_plugins:
			plugin.modify_tasklist(self, manifest)

	def run(self, bootstrap_info):
		for task in self:
			print('Running {taskname}'.format(taskname=task))
			task.run(bootstrap_info)

	def before(self, ref, task):
		i = next(i for i, task in enumerate(self) if type(task) is ref)
		self.insert(i, task)

	def replace(self, ref, task):
		i = next(i for i, task in enumerate(self) if type(task) is ref)
		self.pop(i)
		self.insert(i, task)

	def after(self, ref, task):
		i = next(i for i, task in enumerate(self) if type(task) is ref)
		self.insert(i+1, task)
