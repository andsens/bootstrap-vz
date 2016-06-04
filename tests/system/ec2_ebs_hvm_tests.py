from manifests import merge_manifest_data
from tools import boot_manifest

partials = {'ebs_hvm': '''
provider:
  name: ec2
  virtualization: hvm
  description: Debian {system.release} {system.architecture}
volume: {backing: ebs}
''',
            'extlinux': 'system: {bootloader: extlinux}',
            'grub': 'system: {bootloader: grub}',
            }


def test_unpartitioned_extlinux_oldstable():
    std_partials = ['base', 'oldstable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_extlinux_oldstable():
    std_partials = ['base', 'oldstable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_extlinux_oldstable():
    std_partials = ['base', 'oldstable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_unpartitioned_extlinux_stable():
    std_partials = ['base', 'stable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_extlinux_stable():
    std_partials = ['base', 'stable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_extlinux_stable():
    std_partials = ['base', 'stable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_grub_stable():
    std_partials = ['base', 'stable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['grub']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_grub_stable():
    std_partials = ['base', 'stable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['grub']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_unpartitioned_extlinux_unstable():
    std_partials = ['base', 'unstable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_extlinux_unstable():
    std_partials = ['base', 'unstable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_extlinux_unstable():
    std_partials = ['base', 'unstable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['extlinux']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_msdos_grub_unstable():
    std_partials = ['base', 'unstable64', 'msdos', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['grub']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_gpt_grub_unstable():
    std_partials = ['base', 'unstable64', 'gpt', 'single_partition', 'root_password']
    custom_partials = [partials['ebs_hvm'], partials['grub']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 't2.micro'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)
