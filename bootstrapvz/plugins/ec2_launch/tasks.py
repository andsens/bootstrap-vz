import logging
from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.providers.ec2.tasks import ami


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
        r = conn.run_instances(ImageId=info._ec2['image']['ImageId'],
                               MinCount=1,
                               MaxCount=1,
                               SecurityGroupIds=info.manifest.plugins['ec2_launch'].get('security_group_ids'),
                               KeyName=info.manifest.plugins['ec2_launch'].get('ssh_key'),
                               InstanceType=info.manifest.plugins['ec2_launch'].get('instance_type',
                                                                                    'm3.medium'))
        info._ec2['instance'] = r['Instances'][0]

        if 'tags' in info.manifest.plugins['ec2_launch']:
            raw_tags = info.manifest.plugins['ec2_launch']['tags']
            formatted_tags = {k: v.format(**info.manifest_vars) for k, v in raw_tags.items()}
            tags = [{'Key': k, 'Value': v} for k, v in formatted_tags.items()]
            conn.create_tags(Resources=[info._ec2['instance']['InstanceId']],
                             Tags=tags)


class PrintPublicIPAddress(Task):
    description = 'Waiting for the instance to launch'
    phase = phases.image_registration
    predecessors = [LaunchEC2Instance]

    @classmethod
    def run(cls, info):
        conn = info._ec2['connection']
        logger = logging.getLogger(__name__)
        filename = info.manifest.plugins['ec2_launch']['print_public_ip']
        if not filename:
            filename = '/dev/null'
        f = open(filename, 'w')

        try:
            waiter = conn.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[info._ec2['instance']['InstanceId']],
                        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            info._ec2['instance'] = conn.describe_instances(InstanceIds=[info._ec2['instance']['InstanceId']])['Reservations'][0]['Instances'][0]
            logger.info('******* EC2 IP ADDRESS: %s *******' % info._ec2['instance']['PublicIpAddress'])
            f.write(info._ec2['instance']['PublicIpAddress'])
        except:
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
