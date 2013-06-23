import logging
log = logging.getLogger(__name__)


class TaskList(object):

	def __init__(self):
		self.tasks = set()

	def add(self, *args):
		self.tasks.update(args)

	def remove(self, task):
		self.tasks.discard(self.get(task))

	def replace(self, task, replacement):
		self.remove(task)
		self.add(replacement)

	def get(self, task):
		return next(task for task in self.tasks if type(task) is ref)

	def run(self, bootstrap_info):
		log.debug('Tasklist before:\n{list}'.format(list=',\n'.join(str(task) for task in self.tasks) ))
		task_list = sorted(self.tasks)
		log.debug('Tasklist:\n{list}'.format(list=',\n'.join(str(task) for task in task_list) ))
		return
		for task in tasks:
			log.info(task)
			task.run(bootstrap_info)
