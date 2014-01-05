from base import Task
from common import phases


class TriggerRollback(Task):
	phase = phases.cleaning

	description = 'Triggering a rollback by throwing an exception'

	def run(self, info):
		from common.exceptions import TaskError
		raise TaskError('Trigger rollback')
