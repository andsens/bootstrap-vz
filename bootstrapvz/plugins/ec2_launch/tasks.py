from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.ec2.tasks import ami
import logging


# TODO: Merge with the method available in wip-integration-tests branch
def waituntil(predicate, timeout=5, interval=0.05):
	import time
	threshhold = time.time() + timeout
	while time.time() < threshhold:
		if predicate():
			return True
		time.sleep(interval)
	return False


class LaunchEC2Instance(Task):
    description = 'Launching EC2 instance'
    phase = phases.image_registration
    predecessors = [ami.RegisterAMI]

    @classmethod
    def run(cls, info):
        conn = info._ec2['connection']
        r = conn.run_instances(info._ec2['image'],
                               security_group_ids=info.manifest.plugins['ec2_launch'].get('security_group_ids'),
                               instance_type=info.manifest.plugins['ec2_launch'].get('instance_type', 't2.micro'))
        info._ec2['instance_id'] = r.instances[0].id

        if 'tags' in info.manifest.plugins['ec2_launch']:
            def apply_format(v):
                return v.format(**info.manifest_vars)
            tags = info.manifest.plugins['ec2_launch']['tags']
            r = {k: apply_format(v) for k, v in tags.items()}
            conn.create_tags([info._ec2['instance_id']], r)


class PrintPublicIPAddress(Task):
    description = 'Waiting for the instance to launch'
    phase = phases.image_registration
    predecessors = [LaunchEC2Instance]

    @classmethod
    def run(cls, info):
        ec2 = info._ec2
        logger = logging.getLogger(__name__)
        filename = info.manifest.plugins['ec2_launch']['print_public_ip']
        if not filename:
            filename = '/dev/null'
        f = open(filename, 'w')

        r = ec2['connection'].get_only_instances([ec2['instance_id']])
        if not r and not r[0]:
            logger.error('Could not get instance metadata')
            f.write('')
        else:
            instance = r[0]

            def instance_has_ip():
                instance.update()
                return instance.ip_address

            if waituntil(instance_has_ip, timeout=120, interval=5):
                logger.info('******* EC2 IP ADDRESS: %s *******' % instance.ip_address)
                f.write(instance.ip_address)
            else:
                logger.error('Could not get IP address for the instance')
                f.write('')

        f.close()
