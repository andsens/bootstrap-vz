import virtualbox
from contextlib import contextmanager
from tests.system.tools import waituntil
import logging
log = logging.getLogger(__name__)


class VirtualBoxInstance(object):

    cpus = 1
    memory = 256

    def __init__(self, image, name, arch, release):
        self.image = image
        self.name = name
        self.arch = arch
        self.release = release
        self.vbox = virtualbox.VirtualBox()
        manager = virtualbox.Manager()
        self.session = manager.get_session()

    def create(self):
        log.debug('Creating vbox machine `{name}\''.format(name=self.name))
        # create machine
        os_type = {'x86': 'Debian',
                   'amd64': 'Debian_64'}.get(self.arch)
        self.machine = self.vbox.create_machine(settings_file='', name=self.name,
                                                groups=[], os_type_id=os_type, flags='')
        self.machine.cpu_count = self.cpus
        self.machine.memory_size = self.memory
        self.machine.save_settings()  # save settings, so that we can register it
        self.vbox.register_machine(self.machine)

        # attach image
        log.debug('Attaching SATA storage controller to vbox machine `{name}\''.format(name=self.name))
        with lock(self.machine, self.session) as machine:
            strg_ctrl = machine.add_storage_controller('SATA Controller',
                                                       virtualbox.library.StorageBus.sata)
            strg_ctrl.port_count = 1
            machine.attach_device(name='SATA Controller', controller_port=0, device=0,
                                  type_p=virtualbox.library.DeviceType.hard_disk,
                                  medium=self.image.medium)
            machine.save_settings()

        # redirect serial port
        log.debug('Enabling serial port on vbox machine `{name}\''.format(name=self.name))
        with lock(self.machine, self.session) as machine:
            serial_port = machine.get_serial_port(0)
            serial_port.enabled = True
            import tempfile
            handle, self.serial_port_path = tempfile.mkstemp()
            import os
            os.close(handle)
            serial_port.path = self.serial_port_path
            serial_port.host_mode = virtualbox.library.PortMode.host_pipe
            serial_port.server = True  # Create the socket on startup
            machine.save_settings()

    def boot(self):
        log.debug('Booting vbox machine `{name}\''.format(name=self.name))
        self.machine.launch_vm_process(self.session, 'headless').wait_for_completion(-1)
        from tests.system.tools import read_from_socket
        # Gotta figure out a more reliable way to check when the system is done booting.
        # Maybe bootstrapped unit test images should have a startup script that issues
        # a callback to the host.
        from bootstrapvz.common.releases import wheezy
        if self.release <= wheezy:
            termination_string = 'INIT: Entering runlevel: 2'
        else:
            termination_string = 'Debian GNU/Linux'
        self.console_output = read_from_socket(self.serial_port_path, termination_string, 120)

    def shutdown(self):
        log.debug('Shutting down vbox machine `{name}\''.format(name=self.name))
        self.session.console.power_down().wait_for_completion(-1)
        if not waituntil(lambda: self.machine.session_state == virtualbox.library.SessionState.unlocked):
            raise LockingException('Timeout while waiting for the machine to become unlocked')

    def destroy(self):
        log.debug('Destroying vbox machine `{name}\''.format(name=self.name))
        if hasattr(self, 'machine'):
            try:
                log.debug('Detaching SATA storage controller from vbox machine `{name}\''.format(name=self.name))
                with lock(self.machine, self.session) as machine:
                    machine.detach_device(name='SATA Controller', controller_port=0, device=0)
                    machine.save_settings()
            except virtualbox.library.VBoxErrorObjectNotFound:
                pass
            log.debug('Unregistering and removing vbox machine `{name}\''.format(name=self.name))
            self.machine.unregister(virtualbox.library.CleanupMode.unregister_only)
            self.machine.remove(delete=True)
        else:
            log.debug('vbox machine `{name}\' was not created, skipping destruction'.format(name=self.name))


@contextmanager
def lock(machine, session):
    if machine.session_state != virtualbox.library.SessionState.unlocked:
        msg = ('Acquiring lock on machine failed, state was `{state}\' '
               'instead of `Unlocked\'.'.format(state=str(machine.session_state)))
        raise LockingException(msg)

    machine.lock_machine(session, virtualbox.library.LockType.write)
    yield session.machine

    if machine.session_state != virtualbox.library.SessionState.locked:
        if not waituntil(lambda: machine.session_state == virtualbox.library.SessionState.unlocked):
            msg = ('Error before trying to release lock on machine, state was `{state}\' '
                   'instead of `Locked\'.'.format(state=str(machine.session_state)))
            raise LockingException(msg)

    session.unlock_machine()

    if not waituntil(lambda: machine.session_state == virtualbox.library.SessionState.unlocked):
        msg = ('Timeout while trying to release lock on machine, '
               'last state was `{state}\''.format(state=str(machine.session_state)))
        raise LockingException(msg)


class LockingException(Exception):
    pass
