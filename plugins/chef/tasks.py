from base import Task
from common import phases
from common.tasks import apt
import os


class CheckAssetsPath(Task):
	description = 'Checking whether the assets path exist'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		from common.exceptions import TaskError
		assets = info.manifest.plugins['chef']['assets']
		if not os.path.exists(assets):
			msg = 'The assets directory {assets} does not exist.'.format(assets=assets)
			raise TaskError(msg)
		if not os.path.isdir(assets):
			msg = 'The assets path {assets} does not point to a directory.'.format(assets=assets)
			raise TaskError(msg)


class AddPackages(Task):
	description = 'Add chef package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('chef')


class CopyChefAssets(Task):
	description = 'Copying chef assets'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from shutil import copy
		chef_path = os.path.join(info.root, 'etc/chef')
		chef_assets = info.manifest.plugins['chef']['assets']
		for abs_prefix, dirs, files in os.walk(chef_assets):
			prefix = os.path.normpath(os.path.relpath(abs_prefix, chef_assets))
			for path in dirs:
				full_path = os.path.join(chef_path, prefix, path)
				if os.path.exists(full_path):
					if os.path.isdir(full_path):
						continue
					else:
						os.remove(full_path)
				os.mkdir(full_path)
			for path in files:
				copy(os.path.join(abs_prefix, path),
				     os.path.join(chef_path, prefix, path))

