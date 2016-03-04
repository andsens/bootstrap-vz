Open Nebula
-----------

This plugin adds `OpenNebula
contextualization <http://opennebula.org/documentation:rel4.2:cong>`__
to the image, which sets up the network configuration and SSH keys.

The virtual machine context should be configured as follows:

.. code-block:: text

  ETH0_DNS      $NETWORK[DNS, NETWORK_ID=2]
  ETH0_GATEWAY  $NETWORK[GATEWAY, NETWORK_ID=2]
  ETH0_IP       $NIC[IP, NETWORK_ID=2]
  ETH0_MASK     $NETWORK[MASK, NETWORK_ID=2]
  ETH0_NETWORK  $NETWORK[NETWORK, NETWORK_ID=2]
  FILES         path_to_my_ssh_public_key.pub

The plugin will install all *.pub* files in the root authorized\_keys
file. When using the ec2 provider, the USER\_EC2\_DATA will be executed
if present.

Settings
~~~~~~~~

This plugin has no settings. To enable it add ``"opennebula":{}`` to the
plugin section of the manifest.
