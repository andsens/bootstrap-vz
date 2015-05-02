from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import kernel
from . import assets
import os.path


class AdjustExpandRootDev(Task):
	description = 'Adjusting the expand-root device'
	phase = phases.system_modification
	predecessors = [initd.AddExpandRoot, initd.AdjustExpandRootScript]

	@classmethod
	def run(cls, info):
		from bootstrapvz.common.tools import sed_i
		script = os.path.join(info.root, 'etc/init.d/expand-root')
		sed_i(script, '/dev/xvda', '/dev/sda')


class AddGrowRootDisable(Task):
	description = 'Add script to selectively disable growroot'
	phase = phases.system_modification
	successors = [kernel.UpdateInitramfs]

	@classmethod
	def run(cls, info):
		import stat
		rwxr_xr_x = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
		             stat.S_IRGRP                | stat.S_IXGRP |
		             stat.S_IROTH                | stat.S_IXOTH)
		from shutil import copy
		script_src = os.path.join(assets,
                            'initramfs-tools/scripts/local-premount/gce-disable-growroot')
		script_dst = os.path.join(info.root,
                            'etc/initramfs-tools/scripts/local-premount/gce-disable-growroot')
		copy(script_src, script_dst)
		os.chmod(script_dst, rwxr_xr_x)
