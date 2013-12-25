from base import Task
from common import phases
from plugins.packages.tasks import InstallRemotePackages
from common.tasks import apt
from common.tools import log_check_call
import re


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
		if "metadata_sources" in info.manifest.plugins['cloud_init']:
		    sources = "cloud-init      cloud-init/datasources  multiselect     " + info.manifest.plugins['cloud_init']['metadata_sources']
		    log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/debconf-set-selections'], sources)


class AutoSetMetadataSource(Task):
	description = 'Auto-setting metadata source'
        phase = phases.system_modification
	predecessors = [apt.AptSources]
        successors = [SetMetadataSource]

	def run(self, info):
		sources = ""
		if info.manifest.provider == "ec2":
		  sources = "Ec2"

		if sources:
		  print ("Setting metadata source to " + sources)
		  sources = "cloud-init      cloud-init/datasources  multiselect     " + sources
		  log_check_call(['/usr/sbin/chroot', info.root, '/usr/bin/debconf-set-selections'], sources)


class DisableModules(Task):
	description = 'Setting cloud.cfg modules'
        phase = phases.system_modification
	predecessors = [apt.AptUpgrade]

	def run(self, info):
		if 'disable_modules' in info.manifest.plugins['cloud_init']:
		  patterns = ""
		  for pattern in info.manifest.plugins['cloud_init']['disable_modules']:
		    if patterns != "":
		      patterns = patterns + "|" + pattern
		    else:
		      patterns = "^\s+-\s+(" + pattern
		  patterns = patterns + ")$"
		  regex = re.compile(patterns)

		  try:
		    f = open(info.root + "/etc/cloud/cloud.cfg")
		    lines = f.readlines()
		    f.close()
		  except:
		    print "Cannot read cloud.cfg"
		    return -1

		  f = open(info.root + "/etc/cloud/cloud.cfg", "w")
		  for line in lines:
		    if not regex.match(line):
		      f.write(line)
		  f.close
