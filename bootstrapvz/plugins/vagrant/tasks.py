from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import workspace
from bootstrapvz.common.tools import rel_path
import os
import shutil

assets = rel_path(__file__, 'assets')


class CheckBoxPath(Task):
    description = 'Checking if the vagrant box file already exists'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        box_basename = info.manifest.name.format(**info.manifest_vars)
        box_name = box_basename + '.box'
        box_path = os.path.join(info.manifest.bootstrapper['workspace'], box_name)
        if os.path.exists(box_path):
            from bootstrapvz.common.exceptions import TaskError
            msg = 'The vagrant box `{name}\' already exists at `{path}\''.format(name=box_name, path=box_path)
            raise TaskError(msg)
        info._vagrant['box_name'] = box_name
        info._vagrant['box_path'] = box_path


class CreateVagrantBoxDir(Task):
    description = 'Creating directory for the vagrant box'
    phase = phases.preparation
    predecessors = [workspace.CreateWorkspace]

    @classmethod
    def run(cls, info):
        info._vagrant['folder'] = os.path.join(info.workspace, 'vagrant')
        os.mkdir(info._vagrant['folder'])


class AddPackages(Task):
    description = 'Add packages that vagrant depends on'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('openssh-server')
        info.packages.add('sudo')
        info.packages.add('nfs-client')


class CreateVagrantUser(Task):
    description = 'Creating the vagrant user'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root,
                        'useradd',
                        '--create-home', '--shell', '/bin/bash',
                        'vagrant'])


class PasswordlessSudo(Task):
    description = 'Allowing the vagrant user to use sudo without a password'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        sudo_vagrant_path = os.path.join(info.root, 'etc/sudoers.d/vagrant')
        with open(sudo_vagrant_path, 'w') as sudo_vagrant:
            sudo_vagrant.write('vagrant ALL=(ALL) NOPASSWD:ALL')
        import stat
        ug_read_only = (stat.S_IRUSR | stat.S_IRGRP)
        os.chmod(sudo_vagrant_path, ug_read_only)


class AddInsecurePublicKey(Task):
    description = 'Adding vagrant insecure public key'
    phase = phases.system_modification
    predecessors = [CreateVagrantUser]

    @classmethod
    def run(cls, info):
        ssh_dir = os.path.join(info.root, 'home/vagrant/.ssh')
        os.mkdir(ssh_dir)

        authorized_keys_source_path = os.path.join(assets, 'authorized_keys')
        with open(authorized_keys_source_path, 'r') as authorized_keys_source:
            insecure_public_key = authorized_keys_source.read()

        authorized_keys_path = os.path.join(ssh_dir, 'authorized_keys')
        with open(authorized_keys_path, 'a') as authorized_keys:
            authorized_keys.write(insecure_public_key)

        import stat
        os.chmod(ssh_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.chmod(authorized_keys_path, stat.S_IRUSR | stat.S_IWUSR)

        # We can't do this directly with python, since getpwnam gets its info from the host
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root,
                        'chown', 'vagrant:vagrant',
                        '/home/vagrant/.ssh', '/home/vagrant/.ssh/authorized_keys'])


class SetRootPassword(Task):
    description = 'Setting the root password to `vagrant\''
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call
        log_check_call(['chroot', info.root, 'chpasswd'], 'root:vagrant')


class PackageBox(Task):
    description = 'Packaging the volume as a vagrant box'
    phase = phases.image_registration

    @classmethod
    def run(cls, info):
        vagrantfile_source = os.path.join(assets, 'Vagrantfile')
        vagrantfile = os.path.join(info._vagrant['folder'], 'Vagrantfile')
        shutil.copy(vagrantfile_source, vagrantfile)

        import random
        mac_address = '080027{mac:06X}'.format(mac=random.randrange(16 ** 6))
        from bootstrapvz.common.tools import sed_i
        sed_i(vagrantfile, '\\[MAC_ADDRESS\\]', mac_address)

        metadata_source = os.path.join(assets, 'metadata.json')
        metadata = os.path.join(info._vagrant['folder'], 'metadata.json')
        shutil.copy(metadata_source, metadata)

        from bootstrapvz.common.tools import log_check_call
        disk_name = 'box-disk1.' + info.volume.extension
        disk_link = os.path.join(info._vagrant['folder'], disk_name)
        log_check_call(['ln', '-s', info.volume.image_path, disk_link])

        ovf_path = os.path.join(info._vagrant['folder'], 'box.ovf')
        cls.write_ovf(info, ovf_path, mac_address, disk_name)

        box_files = os.listdir(info._vagrant['folder'])
        log_check_call(['tar', '--create', '--gzip', '--dereference',
                        '--file', info._vagrant['box_path'],
                        '--directory', info._vagrant['folder']] + box_files
                       )
        import logging
        logging.getLogger(__name__).info('The vagrant box has been placed at ' + info._vagrant['box_path'])

    @classmethod
    def write_ovf(cls, info, destination, mac_address, disk_name):
        namespaces = {'ovf':     'http://schemas.dmtf.org/ovf/envelope/1',
                      'rasd':    'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData',
                      'vssd':    'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData',
                      'xsi':     'http://www.w3.org/2001/XMLSchema-instance',
                      'vbox':    'http://www.virtualbox.org/ovf/machine',
                      }

        def attr(element, name, value=None):
            for prefix, ns in namespaces.iteritems():
                name = name.replace(prefix + ':', '{' + ns + '}')
            if value is None:
                return element.attrib[name]
            else:
                element.attrib[name] = str(value)

        template_path = os.path.join(assets, 'box.ovf')
        import xml.etree.ElementTree as ET
        template = ET.parse(template_path)
        root = template.getroot()

        [disk_ref] = root.findall('./ovf:References/ovf:File', namespaces)
        attr(disk_ref, 'ovf:href', disk_name)

        # List of OVF disk format URIs
        # Snatched from VBox source (src/VBox/Main/src-server/ApplianceImpl.cpp:47)
        # ISOURI = "http://www.ecma-international.org/publications/standards/Ecma-119.htm"
        # VMDKStreamURI = "http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized"
        # VMDKSparseURI = "http://www.vmware.com/specifications/vmdk.html#sparse"
        # VMDKCompressedURI = "http://www.vmware.com/specifications/vmdk.html#compressed"
        # VMDKCompressedURI2 = "http://www.vmware.com/interfaces/specifications/vmdk.html#compressed"
        # VHDURI = "http://go.microsoft.com/fwlink/?LinkId=137171"
        volume_uuid = info.volume.get_uuid()
        [disk] = root.findall('./ovf:DiskSection/ovf:Disk', namespaces)
        attr(disk, 'ovf:capacity', info.volume.size.bytes.get_qty_in('B'))
        attr(disk, 'ovf:format', info.volume.ovf_uri)
        attr(disk, 'vbox:uuid', volume_uuid)

        [system] = root.findall('./ovf:VirtualSystem', namespaces)
        attr(system, 'ovf:id', info._vagrant['box_name'])

        # Set the operating system
        [os_section] = system.findall('./ovf:OperatingSystemSection', namespaces)
        os_info = {'i386': {'id': 96, 'name': 'Debian'},
                   'amd64': {'id': 96, 'name': 'Debian_64'}
                   }.get(info.manifest.system['architecture'])
        attr(os_section, 'ovf:id', os_info['id'])
        [os_desc] = os_section.findall('./ovf:Description', namespaces)
        os_desc.text = os_info['name']
        [os_type] = os_section.findall('./vbox:OSType', namespaces)
        os_type.text = os_info['name']

        [sysid] = system.findall('./ovf:VirtualHardwareSection/ovf:System/'
                                 'vssd:VirtualSystemIdentifier', namespaces)
        sysid.text = info._vagrant['box_name']

        [machine] = system.findall('./vbox:Machine', namespaces)
        import uuid
        attr(machine, 'ovf:uuid', uuid.uuid4())
        attr(machine, 'ovf:name', info._vagrant['box_name'])
        from datetime import datetime
        attr(machine, 'ovf:lastStateChange', datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
        [nic] = machine.findall('./ovf:Hardware/ovf:Network/ovf:Adapter', namespaces)
        attr(machine, 'ovf:MACAddress', mac_address)

        [device_img] = machine.findall('./ovf:StorageControllers'
                                       '/ovf:StorageController[@name="SATA Controller"]'
                                       '/ovf:AttachedDevice/ovf:Image', namespaces)
        attr(device_img, 'uuid', '{' + str(volume_uuid) + '}')

        template.write(destination, xml_declaration=True)  # , default_namespace=namespaces['ovf']


class RemoveVagrantBoxDir(Task):
    description = 'Removing the vagrant box directory'
    phase = phases.cleaning
    successors = [workspace.DeleteWorkspace]

    @classmethod
    def run(cls, info):
        shutil.rmtree(info._vagrant['folder'])
        del info._vagrant['folder']
