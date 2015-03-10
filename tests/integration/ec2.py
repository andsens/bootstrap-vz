from manifests import merge_manifest_data
from tools import boot_manifest

partials = {'ec2': 'provider: {name: ec2}',
            'ebs': 'volume: {backing: ebs}',
            's3': 'volume: {backing: s3}',
            'pvm': '{provider: {virtualization: pvm}, system: {bootloader: pvgrub}}',
            'hvm-extlinux': '{provider: {virtualization: hvm}, system: {bootloader: extlinux}}',
            'hvm-grub': '{provider: {virtualization: hvm}, system: {bootloader: grub}}',
            }


def test_unpartitioned_ebs_pvgrub_stable():
	std_partials = ['base', 'stable64', 'unpartitioned', 'root_password']
	custom_partials = [partials['ec2'], partials['ebs'], partials['pvm']]
	manifest_data = merge_manifest_data(std_partials, custom_partials)
	boot_vars = {'instance_type': 't1.micro'}
	with boot_manifest(manifest_data, boot_vars) as instance:
		print(instance.get_console_output().output)
