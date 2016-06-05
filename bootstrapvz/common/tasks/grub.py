from bootstrapvz.base import Task
from ..exceptions import TaskError
from .. import phases
from ..tools import log_check_call
import filesystem
import kernel
from bootstrapvz.base.fs import partitionmaps
import os.path


class AddGrubPackage(Task):
    description = 'Adding grub package'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('grub-pc')


class InitGrubConfig(Task):
    description = 'Initializing grub standard configuration'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        # The default values and documentation below was fetched from
        # https://www.gnu.org/software/grub/manual/html_node/Simple-configuration.html
        # Some explanations have been shortened
        info.grub_config = {
            # The default menu entry. This may be a number, in which case it identifies the Nth entry
            # in the generated menu counted from zero, or the title of a menu entry,
            # or the special string `saved'. Using the title may be useful if you want to set a menu entry
            # as the default even though there may be a variable number of entries before it.
            # If you set this to `saved', then the default menu entry will be that
            # saved by `GRUB_SAVEDEFAULT', grub-set-default, or grub-reboot.
            # The default is `0'.
            'GRUB_DEFAULT': 0,

            # If this option is set to `true', then, when an entry is selected,
            # save it as a new default entry for use by future runs of GRUB.
            # This is only useful if `GRUB_DEFAULT=saved';
            # it is a separate option because `GRUB_DEFAULT=saved' is useful without this option,
            # in conjunction with grub-set-default or grub-reboot. Unset by default.
            'GRUB_SAVEDEFAULT': None,

            # Boot the default entry this many seconds after the menu is displayed, unless a key is pressed.
            # The default is `5'. Set to `0' to boot immediately without displaying the menu,
            # or to `-1' to wait indefinitely.
            'GRUB_TIMEOUT': 5,

            # Wait this many seconds for a key to be pressed before displaying the menu.
            # If no key is pressed during that time, display the menu for the number of seconds specified
            # in GRUB_TIMEOUT before booting the default entry.
            # We expect that most people who use GRUB_HIDDEN_TIMEOUT will want to have GRUB_TIMEOUT set to `0'
            # so that the menu is not displayed at all unless a key is pressed. Unset by default.
            'GRUB_HIDDEN_TIMEOUT': None,

            # In conjunction with `GRUB_HIDDEN_TIMEOUT', set this to `true' to suppress the verbose countdown
            # while waiting for a key to be pressed before displaying the menu. Unset by default.
            'GRUB_HIDDEN_TIMEOUT_QUIET': None,

            # Variants of the corresponding variables without the `_BUTTON' suffix,
            # used to support vendor-specific power buttons. See Vendor power-on keys.
            'GRUB_DEFAULT_BUTTON': None,
            'GRUB_TIMEOUT_BUTTON': None,
            'GRUB_HIDDEN_TIMEOUT_BUTTON': None,
            'GRUB_BUTTON_CMOS_ADDRESS': None,

            # Set by distributors of GRUB to their identifying name.
            # This is used to generate more informative menu entry titles.
            'GRUB_DISTRIBUTOR': None,

            # Select the terminal input device. You may select multiple devices here, separated by spaces.
            # Valid terminal input names depend on the platform, but may include
            # `console' (PC BIOS and EFI consoles),
            # `serial' (serial terminal),
            # `ofconsole' (Open Firmware console),
            # `at_keyboard' (PC AT keyboard, mainly useful with Coreboot),
            # or `usb_keyboard' (USB keyboard using the HID Boot Protocol,
            # for cases where the firmware does not handle this).
            # The default is to use the platform's native terminal input.
            'GRUB_TERMINAL_INPUT': None,

            # Select the terminal output device. You may select multiple devices here, separated by spaces.
            # Valid terminal output names depend on the platform, but may include
            # `console' (PC BIOS and EFI consoles),
            # `serial' (serial terminal),
            # `gfxterm' (graphics-mode output),
            # `ofconsole' (Open Firmware console),
            # or `vga_text' (VGA text output, mainly useful with Coreboot).
            # The default is to use the platform's native terminal output.
            'GRUB_TERMINAL_OUTPUT': None,

            # If this option is set, it overrides both `GRUB_TERMINAL_INPUT' and `GRUB_TERMINAL_OUTPUT'
            # to the same value.
            'GRUB_TERMINAL': None,

            # A command to configure the serial port when using the serial console.
            # See serial. Defaults to `serial'.
            'GRUB_SERIAL_COMMAND': 'serial',

            # Command-line arguments to add to menu entries for the Linux kernel.
            'GRUB_CMDLINE_LINUX': [],

            # Unless `GRUB_DISABLE_RECOVERY' is set to `true',
            # two menu entries will be generated for each Linux kernel:
            # one default entry and one entry for recovery mode.
            # This option lists command-line arguments to add only to the default menu entry,
            # after those listed in `GRUB_CMDLINE_LINUX'.
            'GRUB_CMDLINE_LINUX_DEFAULT': [],

            # As `GRUB_CMDLINE_LINUX' and `GRUB_CMDLINE_LINUX_DEFAULT', but for NetBSD.
            'GRUB_CMDLINE_NETBSD': [],
            'GRUB_CMDLINE_NETBSD_DEFAULT': [],

            # As `GRUB_CMDLINE_LINUX', but for GNU Mach.
            'GRUB_CMDLINE_GNUMACH': [],

            # The values of these options are appended to the values of
            # `GRUB_CMDLINE_LINUX' and `GRUB_CMDLINE_LINUX_DEFAULT'
            # for Linux and Xen menu entries.
            'GRUB_CMDLINE_XEN': [],
            'GRUB_CMDLINE_XEN_DEFAULT': [],

            # The values of these options replace the values of
            # `GRUB_CMDLINE_LINUX' and `GRUB_CMDLINE_LINUX_DEFAULT' for Linux and Xen menu entries.
            'GRUB_CMDLINE_LINUX_XEN_REPLACE': [],
            'GRUB_CMDLINE_LINUX_XEN_REPLACE_DEFAULT': [],

            # Normally, grub-mkconfig will generate menu entries that use
            # universally-unique identifiers (UUIDs) to identify the root filesystem to the Linux kernel,
            # using a `root=UUID=...' kernel parameter. This is usually more reliable,
            # but in some cases it may not be appropriate.
            # To disable the use of UUIDs, set this option to `true'.
            'GRUB_DISABLE_LINUX_UUID': None,

            # If this option is set to `true', disable the generation of recovery mode menu entries.
            'GRUB_DISABLE_RECOVERY': None,

            # If graphical video support is required, either because the `gfxterm' graphical terminal is
            # in use or because `GRUB_GFXPAYLOAD_LINUX' is set,
            # then grub-mkconfig will normally load all available GRUB video drivers and
            # use the one most appropriate for your hardware.
            # If you need to override this for some reason, then you can set this option.
            # After grub-install has been run, the available video drivers are listed in /boot/grub/video.lst.
            'GRUB_VIDEO_BACKEND': None,

            # Set the resolution used on the `gfxterm' graphical terminal.
            # Note that you can only use modes which your graphics card supports
            # via VESA BIOS Extensions (VBE), so for example native LCD panel resolutions
            # may not be available.
            # The default is `auto', which tries to select a preferred resolution. See gfxmode.
            'GRUB_GFXMODE': 'auto',

            # Set a background image for use with the `gfxterm' graphical terminal.
            # The value of this option must be a file readable by GRUB at boot time,
            # and it must end with .png, .tga, .jpg, or .jpeg.
            # The image will be scaled if necessary to fit the screen.
            'GRUB_BACKGROUND': None,

            # Set a theme for use with the `gfxterm' graphical terminal.
            'GRUB_THEME': None,

            # Set to `text' to force the Linux kernel to boot in normal text mode,
            # `keep' to preserve the graphics mode set using `GRUB_GFXMODE',
            # `widthxheight'[`xdepth'] to set a particular graphics mode,
            # or a sequence of these separated by commas or semicolons to try several modes in sequence.
            # See gfxpayload.
            # Depending on your kernel, your distribution, your graphics card, and the phase of the moon,
            # note that using this option may cause GNU/Linux to suffer from various display problems,
            # particularly during the early part of the boot sequence.
            # If you have problems, set this option to `text' and GRUB will
            # tell Linux to boot in normal text mode.
            'GRUB_GFXPAYLOAD_LINUX': None,

            # Normally, grub-mkconfig will try to use the external os-prober program, if installed,
            # to discover other operating systems installed on the same system and generate appropriate
            # menu entries for them. Set this option to `true' to disable this.
            'GRUB_DISABLE_OS_PROBER': None,

            # Play a tune on the speaker when GRUB starts.
            # This is particularly useful for users unable to see the screen.
            # The value of this option is passed directly to play.
            'GRUB_INIT_TUNE': None,

            # If this option is set, GRUB will issue a badram command to filter out specified regions of RAM.
            'GRUB_BADRAM': None,

            # This option may be set to a list of GRUB module names separated by spaces.
            # Each module will be loaded as early as possible, at the start of grub.cfg.
            'GRUB_PRELOAD_MODULES': [],
        }


class WriteGrubConfig(Task):
    description = 'Writing grub defaults configuration'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        grub_config_contents = ''
        for key, value in info.grub_config.items():
            if isinstance(value, str):
                grub_config_contents += '{}="{}"\n'.format(key, value)
            elif isinstance(value, int):
                grub_config_contents += '{}={}\n'.format(key, value)
            elif isinstance(value, bool):
                grub_config_contents += '{}="{}"\n'.format(key, str(value).lower())
            elif isinstance(value, list):
                if len(value) > 0:
                    args_list = ' '.join(map(str, value))
                    grub_config_contents += '{}="{}"\n'.format(key, args_list)
            elif value is not None:
                raise TaskError('Don\'t know how to handle type {}, '
                                'when creating grub config'.format(type(value)))
        grub_defaults = os.path.join(info.root, 'etc/default/grub')
        with open(grub_defaults, 'w') as grub_defaults_handle:
            grub_defaults_handle.write(grub_config_contents)


class DisablePNIN(Task):
    description = 'Disabling Predictable Network Interfaces'
    phase = phases.system_modification
    successors = [WriteGrubConfig]

    @classmethod
    def run(cls, info):
        # See issue #245 for more details
        info.grub_config['GRUB_CMDLINE_LINUX'].append('net.ifnames=0')
        info.grub_config['GRUB_CMDLINE_LINUX'].append('biosdevname=0')


class SetGrubTerminalToConsole(Task):
    description = 'Setting the grub terminal to `console\''
    phase = phases.system_modification
    successors = [WriteGrubConfig]

    @classmethod
    def run(cls, info):
        # See issue #245 for more details
        info.grub_config['TERMINAL'] = 'console'


class SetGrubConsolOutputDeviceToSerial(Task):
    description = 'Setting the grub terminal output device to `ttyS0\''
    phase = phases.system_modification
    successors = [WriteGrubConfig]

    @classmethod
    def run(cls, info):
        # See issue #245 for more details
        info.grub_config['GRUB_CMDLINE_LINUX_DEFAULT'].append('console=ttyS0')


class RemoveGrubTimeout(Task):
    description = 'Setting grub menu timeout to 0'
    phase = phases.system_modification
    successors = [WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_TIMEOUT'] = 0
        info.grub_config['GRUB_HIDDEN_TIMEOUT'] = 0
        info.grub_config['GRUB_HIDDEN_TIMEOUT_QUIET'] = True


class DisableGrubRecovery(Task):
    description = 'Disabling the grub recovery menu entry'
    phase = phases.system_modification
    successors = [WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_DISABLE_RECOVERY'] = True


class EnableSystemd(Task):
    description = 'Enabling systemd'
    phase = phases.system_modification
    successors = [WriteGrubConfig]

    @classmethod
    def run(cls, info):
        info.grub_config['GRUB_CMDLINE_LINUX'].append('init=/bin/systemd')


class InstallGrub_1_99(Task):
    description = 'Installing grub 1.99'
    phase = phases.system_modification
    predecessors = [filesystem.FStab, WriteGrubConfig]

    @classmethod
    def run(cls, info):
        p_map = info.volume.partition_map

        # GRUB screws up when installing in chrooted environments
        # so we fake a real harddisk with dmsetup.
        # Guide here: http://ebroder.net/2009/08/04/installing-grub-onto-a-disk-image/
        from ..fs import unmounted
        with unmounted(info.volume):
            info.volume.link_dm_node()
            if isinstance(p_map, partitionmaps.none.NoPartitions):
                p_map.root.device_path = info.volume.device_path
        try:
            [device_path] = log_check_call(['readlink', '-f', info.volume.device_path])
            device_map_path = os.path.join(info.root, 'boot/grub/device.map')
            partition_prefix = 'msdos'
            if isinstance(p_map, partitionmaps.gpt.GPTPartitionMap):
                partition_prefix = 'gpt'
            with open(device_map_path, 'w') as device_map:
                device_map.write('(hd0) {device_path}\n'.format(device_path=device_path))
                if not isinstance(p_map, partitionmaps.none.NoPartitions):
                    for idx, partition in enumerate(info.volume.partition_map.partitions):
                        device_map.write('(hd0,{prefix}{idx}) {device_path}\n'
                                         .format(device_path=partition.device_path,
                                                 prefix=partition_prefix,
                                                 idx=idx + 1))

            # Install grub
            log_check_call(['chroot', info.root, 'grub-install', device_path])
            log_check_call(['chroot', info.root, 'update-grub'])
        finally:
            with unmounted(info.volume):
                info.volume.unlink_dm_node()
                if isinstance(p_map, partitionmaps.none.NoPartitions):
                    p_map.root.device_path = info.volume.device_path


class InstallGrub_2(Task):
    description = 'Installing grub 2'
    phase = phases.system_modification
    predecessors = [filesystem.FStab, WriteGrubConfig]
    # Make sure the kernel image is updated after we have installed the bootloader
    successors = [kernel.UpdateInitramfs]

    @classmethod
    def run(cls, info):
        log_check_call(['chroot', info.root, 'grub-install', info.volume.device_path])
        log_check_call(['chroot', info.root, 'update-grub'])
