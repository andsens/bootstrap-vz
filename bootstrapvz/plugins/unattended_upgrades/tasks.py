from bootstrapvz.base import Task
from bootstrapvz.common import phases


class AddUnattendedUpgradesPackage(Task):
    description = 'Adding `unattended-upgrades\' to the image packages'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        info.packages.add('unattended-upgrades')


class EnablePeriodicUpgrades(Task):
    description = 'Writing the periodic upgrades apt config file'
    phase = phases.system_modification

    @classmethod
    def run(cls, info):
        import os.path
        periodic_path = os.path.join(info.root, 'etc/apt/apt.conf.d/02periodic')
        update_interval = info.manifest.plugins['unattended_upgrades']['update_interval']
        download_interval = info.manifest.plugins['unattended_upgrades']['download_interval']
        upgrade_interval = info.manifest.plugins['unattended_upgrades']['upgrade_interval']
        with open(periodic_path, 'w') as periodic:
            periodic.write(('// Enable the update/upgrade script (0=disable)\n'
                            'APT::Periodic::Enable "1";\n\n'
                            '// Do "apt-get update" automatically every n-days (0=disable)\n'
                            'APT::Periodic::Update-Package-Lists "{update_interval}";\n\n'
                            '// Do "apt-get upgrade --download-only" every n-days (0=disable)\n'
                            'APT::Periodic::Download-Upgradeable-Packages "{download_interval}";\n\n'
                            '// Run the "unattended-upgrade" security upgrade script\n'
                            '// every n-days (0=disabled)\n'
                            '// Requires the package "unattended-upgrades" and will write\n'
                            '// a log in /var/log/unattended-upgrades\n'
                            'APT::Periodic::Unattended-Upgrade "{upgrade_interval}";\n'
                            .format(update_interval=update_interval,
                                    download_interval=download_interval,
                                    upgrade_interval=upgrade_interval)))
