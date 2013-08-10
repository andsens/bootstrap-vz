# Open Nebula provider

This provider adds OpenNebula contextualization to the virtual image (see http://opennebula.org/documentation:rel4.2:cong).

It set ups the network and ssh keys. TO do so you should configure your virtual machine context with something like:

    ETH0_DNS            $NETWORK[DNS, NETWORK_ID=2]
    ETH0_GATEWAY        $NETWORK[GATEWAY, NETWORK_ID=2]
    ETH0_IP             $NIC[IP, NETWORK_ID=2]
    ETH0_MASK	        $NETWORK[MASK, NETWORK_ID=2]
    ETH0_NETWORK        $NETWORK[NETWORK, NETWORK_ID=2]
    FILES               path_to_my_ssh_public_key.pub

Provider will install all *.pub* files in the root authorized_keys file.

In case of an EC2 start, if the USER_EC2_DATA element is a script it will be executed.
