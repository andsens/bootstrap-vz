from manifests import merge_manifest_data
from tools import boot_manifest

partials = {'vdi': '{provider: {name: virtualbox}, volume: {backing: vdi}}',
            'vmdk': '{provider: {name: virtualbox}, volume: {backing: vmdk}}',
            }


def test_unpartitioned_extlinux_oldstable():
    std_partials = ['base', 'oldstable64', 'extlinux', 'unpartitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_msdos_extlinux_oldstable():
    std_partials = ['base', 'oldstable64', 'extlinux', 'msdos', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_gpt_extlinux_oldstable():
    std_partials = ['base', 'oldstable64', 'extlinux', 'gpt', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_unpartitioned_extlinux_stable():
    std_partials = ['base', 'stable64', 'extlinux', 'unpartitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_msdos_extlinux_stable():
    std_partials = ['base', 'stable64', 'extlinux', 'msdos', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_gpt_extlinux_stable():
    std_partials = ['base', 'stable64', 'extlinux', 'gpt', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_msdos_grub_stable():
    std_partials = ['base', 'stable64', 'grub', 'msdos', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_gpt_grub_stable():
    std_partials = ['base', 'stable64', 'grub', 'gpt', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_unpartitioned_extlinux_unstable():
    std_partials = ['base', 'unstable64', 'extlinux', 'unpartitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_msdos_extlinux_unstable():
    std_partials = ['base', 'unstable64', 'extlinux', 'msdos', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_gpt_extlinux_unstable():
    std_partials = ['base', 'unstable64', 'extlinux', 'gpt', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_msdos_grub_unstable():
    std_partials = ['base', 'unstable64', 'grub', 'msdos', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)


def test_gpt_grub_unstable():
    std_partials = ['base', 'unstable64', 'grub', 'gpt', 'partitioned', 'root_password']
    custom_partials = [partials['vmdk']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print(instance.console_output)
