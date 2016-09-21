ec2-launch
----------
This plugin is spinning up **AWS classic instance** from the AMI created with
the template from which this plugin is invoked.

Settings
~~~~~~~~
- ``security_group_ids``: A list of security groups (not VPC) to attach to the
  instance
  ``required``
- ``instance_type``: A string with AWS Classic capable instance to run
  (default: m3.medium)
  ``optional``
- ``ssh_key``: A string with the ssh key name to apply to the instance.
  ``required``
- ``print_public_ip``: A string with the path to write instance external IP to
  ``optional``
- ``tags``:
  ``optional``
- ``deregister_ami``: A boolean value describing if AMI should be kept after
  sinning up instance or not (default: false)
  ``optional``
