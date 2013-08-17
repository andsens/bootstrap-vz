from base import Task
from common import phases
from common.tasks.packages import ImagePackages
from common.tasks.initd import InstallInitScripts
from common.tasks.apt import AptUpgrade
from common.tasks.apt import AptSources
import os


class AptSourcesBackports(Task):
        description = 'Adding backports to sources.list'
        phase = phases.system_modification
	after = [AptSources]
	before = [AptUpgrade]
        def run(self, info):
                sources_path = os.path.join(info.root, 'etc/apt/sources.list')
                with open(sources_path, 'a') as apt_sources:
                        apt_sources.write(('deb     {apt_mirror} {release}-backports main\n'
                                           'deb-src {apt_mirror} {release}-backports main\n'
                                          .format(apt_mirror='http://http.debian.net/debian',
                                                release=info.manifest.system['release'])))


class AddBackportsPackages(Task):
        description = 'Adding backport packages to the image'
        phase = phases.system_modification
        after = [AptUpgrade]


        def run(self, info):
                if 'packages' not in info.manifest.plugins['backports']:
                        return

                from shutil import copy
                from common.tools import log_check_call

                for pkg in info.manifest.plugins['backports']['packages']:
                        log_check_call(['/usr/sbin/chroot', info.root, 'apt-get', 'install', '-y', '-t', info.manifest.system['release'] + '-backports', pkg])
