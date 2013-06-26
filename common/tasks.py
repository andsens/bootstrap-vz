from base import Task
import phases


class TriggerRollback(Task):
	phase = phases.cleaning

	description = 'Triggering a rollback by throwing an exception'

	def run(self, info):
		from common.exceptions import TaskException
		raise TaskException('Trigger rollback')
