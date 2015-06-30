from bootstrapvz.base import Task
from .. import phases
from ..tools import log_check_call
from . import assets
import os.path


class InstallInitScripts(Task):
	description = 'Installing startup scripts'
	phase = phases.system_modification

	@classmethod
	def run(cls, info):
		import stat
		rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		             stat.S_IRGRP                | stat.S_IXGRP |
		             stat.S_IROTH                | stat.S_IXOTH)
		from shutil import copy
		for name, src in info.initd['install'].iteritems():
			dst = os.path.join(info.root, 'etc/init.d', name)
			copy(src, dst)
			os.chmod(dst, rwxr_xr_x)
			log_check_call(['chroot', info.root, 'insserv', '--default', name])

		for name in info.initd['disable']:
			log_check_call(['chroot', info.root, 'insserv', '--remove', name])


class AddExpandRoot(Task):
	description = 'Adding init script to expand the root volume'
	phase = phases.system_modification
	successors = [InstallInitScripts]

	@classmethod
	def run(cls, info):
		init_scripts_dir = os.path.join(assets, 'init.d')
		info.initd['install']['expand-root'] = os.path.join(init_scripts_dir, 'expand-root')


class RemoveHWClock(Task):
	description = 'Removing hardware clock init scripts'
	phase = phases.system_modification
	successors = [InstallInitScripts]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.releases import squeeze
		info.initd['disable'].append('hwclock.sh')
		if info.manifest.release == squeeze:
			info.initd['disable'].append('hwclockfirst.sh')


class AdjustExpandRootScript(Task):
	description = 'Adjusting the expand-root script'
	phase = phases.system_modification
	predecessors = [InstallInitScripts]

	@classmethod
	def run(cls, info):
		from ..tools import sed_i
		script = os.path.join(info.root, 'etc/init.d/expand-root')
		root_idx = info.volume.partition_map.root.get_index()
		root_index_line = 'root_index="{idx}"'.format(idx=root_idx)
		sed_i(script, '^root_index="0"$', root_index_line)
