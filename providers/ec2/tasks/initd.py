from base import Task
from common import phases
from common.exceptions import TaskError
from common.tasks import initd
import os.path


class AddEC2InitScripts(Task):
	description = 'Adding EC2 startup scripts'
	phase = phases.system_modification
	predecessors = [initd.ResolveInitScripts]
	successors = [initd.InstallInitScripts]

	def run(self, info):
		init_scripts = {'ec2-get-credentials': 'ec2-get-credentials',
		                'ec2-run-user-data': 'ec2-run-user-data'}

		init_scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/init.d'))
		for name, path in init_scripts.iteritems():
			info.initd['install'][name] = os.path.join(init_scripts_dir, path)


class AdjustExpandVolumeScript(Task):
	description = 'Adjusting the expand-volume script'
	phase = phases.system_modification
	predecessors = [initd.InstallInitScripts]

	def run(self, info):
		if 'expand-volume' not in info.initd['install']:
			raise TaskError('The expand-volume script was not installed')

		from base.fs.partitionmaps.none import NoPartitions
		if not isinstance(info.volume.partition_map, NoPartitions):
			import os.path
			from common.tools import sed_i
			script = os.path.join(info.root, 'etc/init.d.expand-volume')
			root_idx = info.volume.partition_map.root.get_index()
			device_path = 'device_path="/dev/xvda{idx}"'.format(idx=root_idx)
			sed_i(script, '^device_path="/dev/xvda$', device_path)
