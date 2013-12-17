from base import Task
from common import phases
from plugins.packages.tasks import InstallRemotePackages
from common.tasks import apt
from common.tools import log_check_call


class SetUsername(Task):
	description = 'Setting username in cloud.cfg'
	phase = phases.system_modification
	predecessors = [InstallRemotePackages]

	def run(self, info):
		from common.tools import sed_i
		import os.path
		cloud_cfg = os.path.join(info.root, 'etc/cloud/cloud.cfg')
		username = info.manifest.plugins['cloud_init']['username']
		search = '^     name: debian$'
		replace = ('     name: {username}\n'
		           '     sudo: ALL=(ALL) NOPASSWD:ALL\n'
		           '     shell: /bin/bash').format(username=username)
		sed_i(cloud_cfg, search, replace)

class SetMetadataSource(Task):
        description = 'Setting metadata source'
        phase = phases.system_modification
	predecessors = [apt.AptSources]
        successors = [apt.AptUpdate]

        def run(self, info):
		sources = "cloud-init      cloud-init/datasources  multiselect     " + info.manifest.plugins['cloud_init']['metadata_sources']
		log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/debconf-set-selections' ], sources)

