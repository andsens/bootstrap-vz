from manifests import merge_manifest_data
from tools.bootable_manifest import BootableManifest
from nose.plugins.skip import Skip

partials = {'vbox': 'provider: {name: virtualbox}',
            'vdi': 'volume: {backing: vdi}',
            'vmdk': 'volume: {backing: vmdk}',
            }


def test_unpartitioned_extlinux_oldstable():
	std_partials = ['base', 'oldstable64', 'extlinux', 'unpartitioned',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_partitioned_extlinux_oldstable():
	std_partials = ['base', 'oldstable64', 'extlinux', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_partitioned_grub_oldstable():
	std_partials = ['base', 'oldstable64', 'grub', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_unpartitioned_extlinux():
	std_partials = ['base', 'stable64', 'extlinux', 'unpartitioned',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_partitioned_extlinux():
	std_partials = ['base', 'stable64', 'extlinux', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_partitioned_grub():
	std_partials = ['base', 'stable64', 'grub', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_unpartitioned_extlinux_unstable():
	raise Skip('Jessie not yet working with extlinux')
	std_partials = ['base', 'unstable64', 'extlinux', 'msdos', 'unpartitioned',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_partitioned_extlinux_unstable():
	raise Skip('Jessie not yet working with extlinux')
	std_partials = ['base', 'unstable64', 'extlinux', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_partitioned_grub_unstable():
	std_partials = ['base', 'unstable64', 'grub', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)
