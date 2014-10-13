from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import initd


class AdjustExpandRootDev(Task):
	description = 'Adjusting the expand-root device'
	phase = phases.system_modification
	predecessors = [initd.AddExpandRoot, initd.AdjustExpandRootScript]

	@classmethod
	def run(cls, info):
		import os.path
		from bootstrapvz.common.tools import sed_i
		script = os.path.join(info.root, 'etc/init.d/expand-root')
		sed_i(script, '/dev/xvda', '/dev/sda')
