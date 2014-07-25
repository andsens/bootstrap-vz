from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tools import sed_i
import os


class CheckAssetsPath(Task):
	description = 'Checking whether the assets path exist'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.exceptions import TaskError
		assets = info.manifest.plugins['puppet']['assets']
		if not os.path.exists(assets):
			msg = 'The assets directory {assets} does not exist.'.format(assets=assets)
			raise TaskError(msg)
		if not os.path.isdir(assets):
			msg = 'The assets path {assets} does not point to a directory.'.format(assets=assets)
			raise TaskError(msg)


class CheckManifestPath(Task):
	description = 'Checking whether the manifest path exist'
	phase = phases.preparation

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.exceptions import TaskError
		manifest = info.manifest.plugins['puppet']['manifest']
		if not os.path.exists(manifest):
			msg = 'The manifest file {manifest} does not exist.'.format(manifest=manifest)
			raise TaskError(msg)
		if not os.path.isfile(manifest):
			msg = 'The manifest path {manifest} does not point to a file.'.format(manifest=manifest)
			raise TaskError(msg)


class AddPackages(Task):
	description = 'Add puppet package'
	phase = phases.preparation
	predecessors = [apt.AddDefaultSources]

	@classmethod
	def run(cls, info):
		info.packages.add('puppet')


class CopyPuppetAssets(Task):
	description = 'Copying puppet assets'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import copy_tree
		copy_tree(info.manifest.plugins['puppet']['assets'], os.path.join(info.root, 'etc/puppet'))


class ApplyPuppetManifest(Task):
	description = 'Applying puppet manifest'
	phase = phases.system_modification
	predecessors = [CopyPuppetAssets]

	@classmethod
	def run(cls, info):
		with open(os.path.join(info.root, 'etc/hostname')) as handle:
			hostname = handle.read().strip()
		with open(os.path.join(info.root, 'etc/hosts'), 'a') as handle:
			handle.write('127.0.0.1\t{hostname}\n'.format(hostname=hostname))

		from shutil import copy
		pp_manifest = info.manifest.plugins['puppet']['manifest']
		manifest_rel_dst = os.path.join('tmp', os.path.basename(pp_manifest))
		manifest_dst = os.path.join(info.root, manifest_rel_dst)
		copy(pp_manifest, manifest_dst)

		manifest_path = os.path.join('/', manifest_rel_dst)
		from bootstrapvz.common.tools import log_check_call
		log_check_call(['chroot', info.root,
		                'puppet', 'apply', manifest_path])
		os.remove(manifest_dst)

		hosts_path = os.path.join(info.root, 'etc/hosts')
		sed_i(hosts_path, '127.0.0.1\s*{hostname}\n?'.format(hostname=hostname), '')


class EnableAgent(Task):
	description = 'Enabling the puppet agent'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		puppet_defaults = os.path.join(info.root, 'etc/defaults/puppet')
		sed_i(puppet_defaults, 'START=no', 'START=yes')
