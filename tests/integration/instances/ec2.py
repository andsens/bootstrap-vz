from contextlib import contextmanager
from ..tools import waituntil
import logging
log = logging.getLogger(__name__)


@contextmanager
def boot_image(image, instance_type, ec2_connection, vpc_connection):

	with create_env(ec2_connection, vpc_connection) as boot_env:

		def waituntil_instance_is(state):
			def instance_has_state():
				instance.update()
				return instance.state == state
			return waituntil(instance_has_state, timeout=600, interval=3)

		instance = None
		try:
			log.debug('Booting ec2 instance')
			reservation = image.run(instance_type=instance_type,
			                        subnet_id=boot_env['subnet_id'])
			[instance] = reservation.instances
			instance.add_tag('Name', 'bootstrap-vz test instance')

			if not waituntil_instance_is('running'):
				raise EC2InstanceStartupException('Timeout while booting instance')

			if not waituntil(lambda: instance.get_console_output().output is not None, timeout=600, interval=3):
				raise EC2InstanceStartupException('Timeout while fetching console output')

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
