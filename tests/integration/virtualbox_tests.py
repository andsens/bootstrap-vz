from manifests import merge_manifest_data
from tools.bootable_manifest import BootableManifest
from nose.plugins.skip import Skip

partials = {'vbox': 'provider: {name: virtualbox}',
            'vdi': 'volume: {backing: vdi}',
            'vmdk': 'volume: {backing: vmdk}',
            }


def test_unpartitioned_extlinux_oldstable():
	std_partials = ['base', 'oldstable64', 'extlinux', 'unpartitioned', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_msdos_extlinux_oldstable():
	std_partials = ['base', 'oldstable64', 'extlinux', 'msdos', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_gpt_extlinux_oldstable():
	std_partials = ['base', 'oldstable64', 'extlinux', 'gpt', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_msdos_grub_oldstable():
	raise Skip('grub install on squeeze is broken')
	std_partials = ['base', 'oldstable64', 'grub', 'msdos', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_gpt_grub_oldstable():
	raise Skip('grub install on squeeze is broken')
	std_partials = ['base', 'oldstable64', 'grub', 'gpt', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_unpartitioned_extlinux():
	std_partials = ['base', 'stable64', 'extlinux', 'unpartitioned', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_msdos_extlinux():
	std_partials = ['base', 'stable64', 'extlinux', 'msdos', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_gpt_extlinux():
	std_partials = ['base', 'stable64', 'extlinux', 'gpt', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_msdos_grub():
	std_partials = ['base', 'stable64', 'grub', 'msdos', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_gpt_grub():
	std_partials = ['base', 'stable64', 'grub', 'gpt', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_unpartitioned_extlinux_unstable():
	std_partials = ['base', 'unstable64', 'extlinux', 'unpartitioned', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_msdos_extlinux_unstable():
	std_partials = ['base', 'unstable64', 'extlinux', 'msdos', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_gpt_extlinux_unstable():
	std_partials = ['base', 'unstable64', 'extlinux', 'gpt', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_msdos_grub_unstable():
	std_partials = ['base', 'unstable64', 'grub', 'msdos', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)


def test_gpt_grub_unstable():
	std_partials = ['base', 'unstable64', 'grub', 'gpt', 'single_partition', 'root_password']
	custom_partials = [partials['vbox'], partials['vmdk']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)
