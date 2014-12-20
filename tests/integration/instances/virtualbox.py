from __future__ import absolute_import
from . import Instance
import virtualbox as vboxapi


class VirtualBoxInstance(Instance):

	cpus = 1
	memory = 256

	def __init__(self, name, image):
		super(VirtualBoxInstance, self).__init__(name, image)
		self.vbox = vboxapi.VirtualBox()
		manager = vboxapi.Manager()
		self.session = manager.get_session()

	def create(self):
		# create machine
		os_type = {'x86': 'Debian',
		           'amd64': 'Debian_64'}.get(self.image.manifest.system['architecture'])
		self.machine = self.vbox.create_machine(settings_file='', name=self.name,
		                                        groups=[], os_type_id=os_type, flags='')
		self.machine.cpu_count = self.cpus
		self.machine.memory_size = self.memory
		self.machine.save_settings()  # save settings, so that we can register it
		self.vbox.register_machine(self.machine)

		# attach image
		with self.Lock(self.machine, self.session) as machine:
			strg_ctrl = machine.add_storage_controller('SATA Controller',
			                                           vboxapi.library.StorageBus.sata)
			strg_ctrl.port_count = 1
			machine.attach_device(name='SATA Controller', controller_port=0, device=0,
			                      type_p=vboxapi.library.DeviceType.hard_disk,
			                      medium=self.image.medium)
			machine.save_settings()

		# redirect serial port
		with self.Lock(self.machine, self.session) as machine:
			serial_port = machine.get_serial_port(0)
			serial_port.enabled = True
			import tempfile
			handle, self.serial_port_path = tempfile.mkstemp()
			import os
			os.close(handle)
			serial_port.path = self.serial_port_path
			serial_port.host_mode = vboxapi.library.PortMode.host_pipe
			serial_port.server = True  # Create the socket on startup
			machine.save_settings()

	def boot(self):
		self.machine.launch_vm_process(self.session, 'headless').wait_for_completion(-1)

	def get_console_output(self):
		import socket
		import select
		import errno
		import sys
		console = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		console.connect(self.serial_port_path)

		console.setblocking(0)
		output = ''
		continue_select = True
		while continue_select:
			read_ready, _, _ = select.select([console], [], [])
			if console in read_ready:
				while True:
					try:
						sys.stdout.write(console.recv(1024))
						break
					except socket.error, e:
						if e.errno != errno.EWOULDBLOCK:
							raise Exception(e)
						continue_select = False
		console.close()
		return output

	def shutdown(self):
		self.session.console.power_down().wait_for_completion(-1)
		self.Lock(self.machine, self.session).unlock()

	def destroy(self):
		if hasattr(self, 'machine'):
			try:
				with self.Lock(self.machine, self.session) as machine:
					machine.detach_device(name='SATA Controller', controller_port=0, device=0)
					machine.save_settings()
			except vboxapi.library.VBoxErrorObjectNotFound:
				pass
			self.machine.unregister(vboxapi.library.CleanupMode.unregister_only)
			self.machine.remove(delete=True)

	class Lock(object):
		def __init__(self, machine, session):
			self.machine = machine
			self.session = session

		def __enter__(self):
			return self.lock()

		def __exit__(self, type, value, traceback):
			return self.unlock()

		def lock(self):
			self.unlock()
			self.machine.lock_machine(self.session, vboxapi.library.LockType.write)
			return self.session.machine

		def unlock(self):
			from ..tools import waituntil
			if self.machine.session_state == vboxapi.library.SessionState.unlocked:
				return
			if self.machine.session_state == vboxapi.library.SessionState.unlocking:
				waituntil(lambda: self.machine.session_state == vboxapi.library.SessionState.unlocked)
				return
			if self.machine.session_state == vboxapi.library.SessionState.spawning:
				waituntil(lambda: self.machine.session_state == vboxapi.library.SessionState.locked)
			self.session.unlock_machine()
			waituntil(lambda: self.machine.session_state == vboxapi.library.SessionState.unlocked)
