from loopbackvolume import LoopbackVolume
from bootstrapvz.base.fs.exceptions import VolumeError
from ..tools import log_check_call
from . import get_partitions


class QEMUVolume(LoopbackVolume):

	def _before_create(self, e):
		self.image_path = e.image_path
		vol_size = str(self.size.get_qty_in('MiB')) + 'M'
		log_check_call(['qemu-img', 'create', '-f', self.qemu_format, self.image_path, vol_size])

	def _check_nbd_module(self):
		from bootstrapvz.base.fs.partitionmaps.none import NoPartitions
		if isinstance(self.partition_map, NoPartitions):
			if not self._module_loaded('nbd'):
				msg = ('The kernel module `nbd\' must be loaded '
				       '(`modprobe nbd\') to attach .{extension} images'
				       .format(extension=self.extension))
				raise VolumeError(msg)
		else:
			num_partitions = len(self.partition_map.partitions)
			if not self._module_loaded('nbd'):
				msg = ('The kernel module `nbd\' must be loaded '
				       '(run `modprobe nbd max_part={num_partitions}\') '
				       'to attach .{extension} images'
				       .format(num_partitions=num_partitions, extension=self.extension))
				raise VolumeError(msg)
			nbd_max_part = int(self._module_param('nbd', 'max_part'))
			if nbd_max_part < num_partitions:
				# Found here: http://bethesignal.org/blog/2011/01/05/how-to-mount-virtualbox-vdi-image/
				msg = ('The kernel module `nbd\' was loaded with the max_part '
				       'parameter set to {max_part}, which is below '
				       'the amount of partitions for this volume ({num_partitions}). '
				       'Reload the nbd kernel module with max_part set to at least {num_partitions} '
				       '(`rmmod nbd; modprobe nbd max_part={num_partitions}\').'
				       .format(max_part=nbd_max_part, num_partitions=num_partitions))
				raise VolumeError(msg)

	def _before_attach(self, e):
		self._check_nbd_module()
		self.loop_device_path = self._find_free_nbd_device()
		log_check_call(['qemu-nbd', '--connect', self.loop_device_path, self.image_path])
		self.device_path = self.loop_device_path

	def _before_detach(self, e):
		log_check_call(['qemu-nbd', '--disconnect', self.loop_device_path])
		del self.loop_device_path
		self.device_path = None

	def _module_loaded(self, module):
		import re
		regexp = re.compile('^{module} +'.format(module=module))
		with open('/proc/modules') as loaded_modules:
			for line in loaded_modules:
				match = regexp.match(line)
				if match is not None:
					return True
		return False

	def _module_param(self, module, param):
		import os.path
		param_path = os.path.join('/sys/module', module, 'parameters', param)
		with open(param_path) as param:
			return param.read().strip()

	# From http://lists.gnu.org/archive/html/qemu-devel/2011-11/msg02201.html
	# Apparently it's not in the current qemu-nbd shipped with wheezy
	def _is_nbd_used(self, device_name):
		return device_name in get_partitions()

	def _find_free_nbd_device(self):
		import os.path
		for i in xrange(0, 15):
			device_name = 'nbd' + str(i)
			if not self._is_nbd_used(device_name):
				return os.path.join('/dev', device_name)
		raise VolumeError('Unable to find free nbd device.')
