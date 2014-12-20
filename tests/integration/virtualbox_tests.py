from manifests import merge_manifest_data
from tools.bootable_manifest import BootableManifest

partials = {'vbox': 'provider: {name: virtualbox}',
            'vdi': 'volume: {backing: vdi}',
            'vmdk': 'volume: {backing: vmdk}',
            }


def test_virtualbox_partitioned_extlinux():
	std_partials = ['base', 'stable64', 'extlinux', 'msdos', 'single_partition',
	                'root_password', 'apt_proxy']
	custom_partials = [partials['vbox'], partials['vdi']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	with BootableManifest(manifest_data) as instance:
		print(instance.console_output)
