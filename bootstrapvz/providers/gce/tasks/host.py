from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import network
import os.path


class DisableIPv6(Task):
    description = "Disabling IPv6 support"
    phase = phases.system_modification
    predecessors = [network.ConfigureNetworkIF]

    @classmethod
    def run(cls, info):
        network_configuration_path = os.path.join(info.root, 'etc/sysctl.d/70-disable-ipv6.conf')
        with open(network_configuration_path, 'w') as config_file:
            print >>config_file, "net.ipv6.conf.all.disable_ipv6 = 1"
            print >>config_file, "net.ipv6.conf.lo.disable_ipv6 = 0"
