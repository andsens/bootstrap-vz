from manifests import merge_manifest_data
from tools import boot_manifest

partials = {'ebs_pvm': '''
provider:
  name: ec2
  virtualization: pvm
  description: Debian {system.release} {system.architecture}
system: {bootloader: pvgrub}
volume: {backing: ebs}
'''
            }


def test_unpartitioned_oldstable():
    std_partials = ['base', 'oldstable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_oldstable():
    std_partials = ['base', 'oldstable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_oldstable():
    std_partials = ['base', 'oldstable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_unpartitioned_stable():
    std_partials = ['base', 'stable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_stable():
    std_partials = ['base', 'stable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_stable():
    std_partials = ['base', 'stable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_unpartitioned_unstable():
    std_partials = ['base', 'unstable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_unstable():
    std_partials = ['base', 'unstable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_unstable():
    std_partials = ['base', 'unstable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't1.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)
