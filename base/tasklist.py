import logging
log = logging.getLogger(__name__)


class TaskList(list):

	def plugins(self, manifest):
		for plugin in manifest.loaded_plugins:
			plugin.modify_tasklist(self, manifest)

	def run(self, bootstrap_info):
		for task in self:
			log.info(task)
			task.run(bootstrap_info)

	def before(self, ref, task):
		log.debug('Inserting %s before %s.%s', task, ref.__module__, ref.__name__)
		i = next(i for i, task in enumerate(self) if type(task) is ref)
		self.insert(i, task)

	def replace(self, ref, task):
		log.debug('Replacing %s.%s with %s', ref.__module__, ref.__name__, task)
		i = next(i for i, task in enumerate(self) if type(task) is ref)
		self.pop(i)
		self.insert(i, task)

	def after(self, ref, task):
		log.debug('Inserting %s after %s.%s', task, ref.__module__, ref.__name__)
		i = next(i for i, task in enumerate(self) if type(task) is ref)
		self.insert(i+1, task)

	def append(self, task):
		super(TaskList, self).append(task)
		log.debug('Appending %s', task)
