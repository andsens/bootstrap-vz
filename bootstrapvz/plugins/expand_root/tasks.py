from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tools import log_check_call
from bootstrapvz.common.tools import rel_path
from bootstrapvz.common.tools import sed_i
import os
import shutil

ASSETS_DIR = rel_path(__file__, 'assets')


class InstallGrowpart(Task):
    description = 'Adding necessary packages for growpart.'
    phase = phases.preparation
    predecessors = [apt.AddBackports]

    @classmethod
    def run(cls, info):
        # Use the cloud-guest-utils package from jessie-backports which has
        # several significant bug fixes from the mainline growpart script.
        target = None
        from bootstrapvz.common.releases import jessie
        if info.manifest.release == jessie:
            target = '{system.release}-backports'
        info.packages.add('cloud-guest-utils', target)


class InstallExpandRootScripts(Task):
    description = 'Installing scripts for expand-root.'
    phase = phases.system_modification
    successors = [initd.InstallInitScripts]

    @classmethod
    def run(cls, info):
        expand_root_script = os.path.join(ASSETS_DIR, 'expand-root')
        expand_root_service = os.path.join(ASSETS_DIR, 'expand-root.service')

        expand_root_script_dest = os.path.join(info.root, 'usr/local/sbin/expand-root')
        expand_root_service_dest = os.path.join(info.root, 'etc/systemd/system/expand-root.service')

        filesystem_type = info.manifest.plugins['expand_root'].get('filesystem_type')
        root_device = info.manifest.plugins['expand_root'].get('root_device')
        root_partition = info.manifest.plugins['expand_root'].get('root_partition')

        # Copy files over
        shutil.copy(expand_root_script, expand_root_script_dest)
        os.chmod(expand_root_script_dest, 0o750)
        shutil.copy(expand_root_service, expand_root_service_dest)

        # Expand out options into expand-root script.
        opts = '%s %s %s' % (root_device, root_partition, filesystem_type)
        sed_i(expand_root_service_dest, r'^ExecStart=/usr/local/sbin/expand-root.*$',
              'ExecStart=/usr/local/sbin/expand-root %s' % opts)

        # Enable systemd service
        log_check_call(['chroot', info.root,  'systemctl', 'enable', 'expand-root.service'])
