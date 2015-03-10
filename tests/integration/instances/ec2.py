from contextlib import contextmanager
from ..tools import waituntil
import logging
log = logging.getLogger(__name__)


@contextmanager
def boot_image(name, image, instance_type):
	instance = None
	try:
		log.debug('Booting ec2 instance')
		reservation = image.run(instance_type=instance_type)
		[instance] = reservation.instances
		instance.add_tag('Name', name)

		def instance_running():
			instance.update()
			return instance.state == 'running'
		if not waituntil(instance_running, timeout=120, interval=3):
			raise EC2InstanceStartupException('Timeout while booting instance')

		if not waituntil(lambda: instance.get_console_output().output is not None, timeout=600, interval=3):
			raise EC2InstanceStartupException('Timeout while fetching console output')

		yield instance
	finally:
		if instance is not None:
			instance.terminate()


class EC2InstanceStartupException(Exception):
	pass
