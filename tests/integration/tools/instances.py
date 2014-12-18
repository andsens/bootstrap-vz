import virtualbox


class Instance(object):

	def __init__(self, name, image):
		self.name = name
		self.image = image

	def boot(self):
		pass

	def shutdown(self):
		pass

	def destroy(self):
		pass


class VirtualBoxInstance(Instance):

	cpus = 1
	memory = 256

	def __init__(self, name, image):
		super(VirtualBoxInstance, self).__init__(name, image)
		self.vbox = virtualbox.VirtualBox()
		manager = virtualbox.Manager()
		self.session = manager.get_session()

	def create(self):
		if self.image.manifest.system['architecture'] == 'x86':
			os_type = 'Debian'
		else:
			os_type = 'Debian_64'
		self.machine = self.vbox.create_machine(settings_file='', name=self.name,
		                                        groups=[], os_type_id=os_type, flags='')
		self.machine.cpu_count = self.cpus
		self.machine.memory_size = self.memory
		self.machine.save_settings()  # save settings, so that we can register it
		self.vbox.register_machine(self.machine)
		self.machine.lock_machine(self.session, virtualbox.library.LockType.write)
		strg_ctrl = self.session.machine.add_storage_controller('SATA Controller',
		                                                        virtualbox.library.StorageBus.sata)
		strg_ctrl.port_count = 1
		self.session.machine.attach_device(name='SATA Controller', controller_port=0, device=0,
		                                   type_p=virtualbox.library.DeviceType.hard_disk,
		                                   medium=self.image.medium)
		self.session.machine.save_settings()  # save changes to the controller
		self._unlock_machine()

	def boot(self):
		self.machine.launch_vm_process(self.session, 'headless').wait_for_completion(-1)

	def shutdown(self):
		self.session.console.power_down().wait_for_completion(-1)
		self._unlock_machine()

	def destroy(self):
		if hasattr(self, 'machine'):
			self.machine.lock_machine(self.session, virtualbox.library.LockType.shared)
			self.session.machine.detach_device(name='SATA Controller', controller_port=0, device=0)
			self.session.machine.save_settings()
			self._unlock_machine()
			self.machine.unregister(virtualbox.library.CleanupMode.unregister_only)
			self.machine.remove(delete=True)

	def _unlock_machine(self):
		from . import waituntil
		self.session.unlock_machine()
		waituntil(lambda: self.machine.session_state != virtualbox.library.SessionState.locked)
