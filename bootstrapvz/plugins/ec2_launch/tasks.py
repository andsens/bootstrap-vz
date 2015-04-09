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
        info._ec2['instance'] = r.instances[0]

        if 'tags' in info.manifest.plugins['ec2_launch']:
            def apply_format(v):
                return v.format(**info.manifest_vars)
            tags = info.manifest.plugins['ec2_launch']['tags']
            r = {k: apply_format(v) for k, v in tags.items()}
            conn.create_tags([info._ec2['instance'].id], r)


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

        def instance_has_ip():
            ec2['instance'].update()
            return ec2['instance'].ip_address

        if waituntil(instance_has_ip, timeout=120, interval=5):
            logger.info('******* EC2 IP ADDRESS: %s *******' % ec2['instance'].ip_address)
            f.write(ec2['instance'].ip_address)
        else:
            logger.error('Could not get IP address for the instance')
            f.write('')

        f.close()


class DeregisterAMI(Task):
    description = 'Deregistering AMI'
    phase = phases.image_registration
    predecessors = [LaunchEC2Instance]

    @classmethod
    def run(cls, info):
        ec2 = info._ec2
        logger = logging.getLogger(__name__)

        def instance_running():
            ec2['instance'].update()
            return ec2['instance'].state == 'running'

        if waituntil(instance_running, timeout=120, interval=5):
            info._ec2['connection'].deregister_image(info._ec2['image'])
            info._ec2['snapshot'].delete()
        else:
            logger.error('Timeout while booting instance')
