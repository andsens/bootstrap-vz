from base import Task
from common import phases
from connection import Connect

class CreateVolume(Task):
	description = 'Creating an EBS volume for bootstrapping'
	phase = phases.volume_creation
	after = [Connect]

	def run(self, info):
		# info.conn.create_volume(50, "us-west-2")
# volume_id=`euca-create-volume --size $volume_size --zone "$availability_zone" | awk '{print $2}'`
# [ -z "$volume_id" ] && die "Unable to create volume."
# log "The EBS volume id is $volume_id"

# 		for package in info.host_packages:
# 			try:
# 				with open(devnull, 'w') as dev_null:
# 					subprocess.check_call(['/usr/bin/dpkg', '-s', package], stdout=dev_null, stderr=dev_null)
# 			except subprocess.CalledProcessError:
# 				msg = "The package ``{0}\'\' is not installed".format(package)
# 				raise RuntimeError(msg)
		pass

