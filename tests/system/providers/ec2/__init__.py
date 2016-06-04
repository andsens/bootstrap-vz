from contextlib import contextmanager
from tests.system.tools import waituntil
import logging
log = logging.getLogger(__name__)


@contextmanager
def prepare_bootstrap(manifest, build_server):
    if manifest.volume['backing'] == 's3':
        credentials = {'access-key': build_server.build_settings['ec2-credentials']['access-key'],
                       'secret-key': build_server.build_settings['ec2-credentials']['secret-key']}
        from boto.s3 import connect_to_region as s3_connect
        s3_connection = s3_connect(manifest.image['region'],
                                   aws_access_key_id=credentials['access-key'],
                                   aws_secret_access_key=credentials['secret-key'])
        log.debug('Creating S3 bucket')
        bucket = s3_connection.create_bucket(manifest.image['bucket'], location=manifest.image['region'])
        try:
            yield
        finally:
            log.debug('Deleting S3 bucket')
            for item in bucket.list():
                bucket.delete_key(item.key)
            s3_connection.delete_bucket(manifest.image['bucket'])
    else:
            yield


@contextmanager
def boot_image(manifest, build_server, bootstrap_info, instance_type=None):

    credentials = {'access-key': build_server.run_settings['ec2-credentials']['access-key'],
                   'secret-key': build_server.run_settings['ec2-credentials']['secret-key']}
    from boto.ec2 import connect_to_region as ec2_connect
    ec2_connection = ec2_connect(bootstrap_info._ec2['region'],
                                 aws_access_key_id=credentials['access-key'],
                                 aws_secret_access_key=credentials['secret-key'])
    from boto.vpc import connect_to_region as vpc_connect
    vpc_connection = vpc_connect(bootstrap_info._ec2['region'],
                                 aws_access_key_id=credentials['access-key'],
                                 aws_secret_access_key=credentials['secret-key'])

    if manifest.volume['backing'] == 'ebs':
        from images import EBSImage
        image = EBSImage(bootstrap_info._ec2['image'], ec2_connection)
    if manifest.volume['backing'] == 's3':
        from images import S3Image
        image = S3Image(bootstrap_info._ec2['image'], ec2_connection)

    try:
        with run_instance(image, manifest, instance_type, ec2_connection, vpc_connection) as instance:
            yield instance
    finally:
        image.destroy()


@contextmanager
def run_instance(image, manifest, instance_type, ec2_connection, vpc_connection):

    with create_env(ec2_connection, vpc_connection) as boot_env:

        def waituntil_instance_is(state):
            def instance_has_state():
                instance.update()
                return instance.state == state
            return waituntil(instance_has_state, timeout=600, interval=3)

        instance = None
        try:
            log.debug('Booting ec2 instance')
            reservation = image.ami.run(instance_type=instance_type,
                                        subnet_id=boot_env['subnet_id'])
            [instance] = reservation.instances
            instance.add_tag('Name', 'bootstrap-vz test instance')

            if not waituntil_instance_is('running'):
                raise EC2InstanceStartupException('Timeout while booting instance')

            if not waituntil(lambda: instance.get_console_output().output is not None, timeout=600, interval=3):
                raise EC2InstanceStartupException('Timeout while fetching console output')

            from bootstrapvz.common.releases import wheezy
            if manifest.release <= wheezy:
                termination_string = 'INIT: Entering runlevel: 2'
            else:
                termination_string = 'Debian GNU/Linux'

            console_output = instance.get_console_output().output
            if termination_string not in console_output:
                last_lines = '\n'.join(console_output.split('\n')[-50:])
                message = ('The instance did not boot properly.\n'
                           'Last 50 lines of console output:\n{output}'.format(output=last_lines))
                raise EC2InstanceStartupException(message)

            yield instance
        finally:
            if instance is not None:
                log.debug('Terminating ec2 instance')
                instance.terminate()
                if not waituntil_instance_is('terminated'):
                    raise EC2InstanceStartupException('Timeout while terminating instance')
                # wait a little longer, aws can be a little slow sometimes and think the instance is still running
                import time
                time.sleep(15)


@contextmanager
def create_env(ec2_connection, vpc_connection):

    vpc_cidr = '10.0.0.0/28'
    subnet_cidr = '10.0.0.0/28'

    @contextmanager
    def vpc():
        log.debug('Creating VPC')
        vpc = vpc_connection.create_vpc(vpc_cidr)
        try:
            yield vpc
        finally:
            log.debug('Deleting VPC')
            vpc_connection.delete_vpc(vpc.id)

    @contextmanager
    def subnet(vpc):
        log.debug('Creating subnet')
        subnet = vpc_connection.create_subnet(vpc.id, subnet_cidr)
        try:
            yield subnet
        finally:
            log.debug('Deleting subnet')
            vpc_connection.delete_subnet(subnet.id)

    with vpc() as _vpc:
        with subnet(_vpc) as _subnet:
            yield {'subnet_id': _subnet.id}


class EC2InstanceStartupException(Exception):
    pass
