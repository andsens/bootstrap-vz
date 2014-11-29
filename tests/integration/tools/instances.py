from bootstrapvz.common.tools import log_check_call


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
		import virtualbox
		self.vbox = virtualbox.VirtualBox()

	def create(self):
		if self.image.manifest['system']['architecture'] == 'x86':
			os_type = 'Debian'
		else:
			os_type = 'Debian_64'
		self.machine = self.vbox.create_machine(settings_file='', name=self.name,
		                                        groups=[], os_type_id=os_type, flags='')
		self.machine.save_settings()
		self.machine.cpu_count = self.cpus
		self.machine.memory_size = self.memory
		self.machine.attach_device(name='root', controller_port=0, device=0,
		                           type_p=self.vbox.library.DeviceType.HardDisk,
		                           medium=self.image.medium)
		self.vbox.register_machine(self.machine)
		# [self.uuid] = log_check_call(['VBoxManage', 'createvm'
		#                               '--name', self.name])
		# log_check_call(['VBoxManage', 'modifyvm', self.uuid,
		#                 '--cpus', self.cpus,
		#                 '--memory', self.memory])
		# log_check_call(['VBoxManage', 'storageattach', self.uuid,
		#                 '--storagectl', '"SATA Controller"',
		#                 '--device', '0',
		#                 '--port', '0',
		#                 '--type', 'hdd',
		#                 '--medium', self.image.image_path])

	def boot(self):
		self.session = self.vbox.Session()
		self.machine.launch_vm_process(self.session, 'headless')
		# log_check_call(['VBoxManage', 'startvm', self.uuid,
		#                 '--type', 'headless'])

	def shutdown(self):
		self.session.console.power_down()
		log_check_call(['VBoxManage', 'stopvm', self.uuid,
		                '--type', 'headless'])

	def destroy(self):
		self.machine.unregister(self.vbox.CleanupMode.full)
		self.machine.remove(delete=True)
