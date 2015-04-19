Remote bootstrapping
====================

bootstrap-vz is able to bootstrap images not only on the machine
on which it is invoked, but also on remote machines that have bootstrap-vz
installed.

This is helpful when you create manifests on your own workstation, but have a
beefed up remote build server which can create images quickly.
There may also be situations where you want to build multiple manifests that
have different providers and require the host machines to be running on
that provider (e.g. EBS backed AMIs can only be created on EC2 instances),
when doing this multiple times SSHing into the machines and copying the
manifests can be a hassle.

Lastly, the main motivation for supporting remote bootstrapping is the
automation of `integration testing <../../tests/integration>`__.
As you will see `further down <#bootstrap-vz-remote>`__,
bootstrap-vz is able to select which build server is required
for a specific test and run the bootstrapping procedure on said server.


bootstrap-vz-remote
-------------------
Normally you'd use ``bootstrap-vz`` to start a bootstrapping process.
When bootstrapping remotely simply use ``bootstrap-vz-remote`` instead,
it takes the same arguments plus a few additional ones:

* ``--servers <path>``: Path to a list of build-servers
  (see `build-servers.yml <#build-servers-yml>`__ for more info)
* ``--name <name>``: Selects a specific build-server from the list
  of build-servers
* ``--release <release>``: Restricts the autoselection of build-servers
  to the ones with the specified release

Much like when bootstrapping directly, you can press ``Ctrl+C`` at any time
to abort the bootstrapping process.
The remote process will receive the keyboard interrupt signal
and begin cleaning up - pressing ``Ctrl+C`` a second time will abort that as
well and kill the connection immediately.

Note that there is also a ``bootstrap-vz-server``, this file is not meant to be
invoked directly by the user, but is instead launched by bootstrap-vz on the
remote server when connecting to it.


Dependencies
------------
For the remote bootstrapping procedure to work, you will need to install
bootstrap-vz as well as the ``sudo`` command on the remote machine.
Also make sure that all the needed dependencies for bootstrapping your image
are installed.

Locally the pip package `Pyro4`__ is needed.

__ https://pypi.python.org/pypi/Pyro4



build-servers.yml
-----------------
The file ``build-servers.yml`` informs bootstrap-vz about the different
build servers you have at your disposal.
In its simplest form you can just add your own machine like this:

.. code:: yaml

  local:
    type: local
    can_bootstrap: [virtualbox]
    release: jessie
    build_settings: {}

``type`` specifies how bootstrap-vz should connect to the build-server.
``local`` simply means that it will call the bootstrapping procedure directly,
no new process is spawned.

``can_bootstrap`` tells bootstrap-vz for which providers this machine is capable
of building images. With the exception of the EC2 provider,
the accepted values match the accepted provider names in the manifest.
For EC2 you can specify ``ec2-s3`` and/or ``ec2-ebs``.
``ec2-ebs`` specifies that the machine in question can bootstrap EBS backed
images and should only be used when the it is located on EC2.
``ec2-s3`` signifies that the machine is capable of bootstrapping S3 backed
images.

Beyond being a string, the value of ``release`` is not enforced in any way.
It's only current use is for ``bootstrap-vz-remote`` where you can restrict
which build-server should be autoselected.


Remote settings
~~~~~~~~~~~~~~~
The other (and more interesting) setting for ``type`` is ``ssh``,
which requires a few more configuration settings:

.. code:: yaml

  local_vm:
    type: ssh
    can_bootstrap:
      - virtualbox
      - ec2-s3
    release: wheezy
    # remote settings below here
    address: 127.0.0.1
    port: 2222
    username: admin
    keyfile: path_to_private_key_file
    server_bin: /root/bootstrap/bootstrap-vz-server


The last 5 settings specify how bootstrap-vz can connect
to the remote build-server.
While the initial handshake is achieved through SSH, bootstrap-vz mainly
communicates with its counterpart through RPC (the communication port is
automatically forwarded through an SSH tunnel).
``address``, ``port``, ``username`` and ``keyfile`` are hopefully
self explanatory (remote machine address, SSH port, login name and path to
private SSH key file).

``server_bin`` refers to the `aboved mentioned <#bootstrap-vz-remote>`__
bootstrap-vz-server executable. This is the command bootstrap-vz executes
on the remote machine to start the RPC server.

Be aware that there are a few limitations as to what bootstrap-vz is able to
deal with, regarding the remote machine setup (in time they may be fixed
by a benevolent contributor):

* The login user must be able to execute sudo without a password
* The private key file must be added to the ssh-agent before invocation
  (alternatively it may not be password protected)
* The server must already be part of the known_hosts list
  (bootstrap-vz uses ``ssh`` directly and cannot handle interactive prompts)


Build settings
~~~~~~~~~~~~~~
The build settings allow you to override specific manifest properties.
This is useful when for example the VirtualBox guest additions ISO is located
at ``/root/guest_additions.iso`` on server 1, while server 2 has it at
``/root/images/vbox.iso``.

.. code:: yaml

  local:
    type: local
    can_bootstrap:
      - virtualbox
      - ec2-s3
    release: jessie
    build_settings:
      guest_additions: /root/images/VBoxGuestAdditions.iso
      apt_proxy:
        address: 127.0.0.1
        port: 3142
      ec2-credentials:
        access-key: AFAKEACCESSKEYFORAWS
        secret-key: thes3cr3tkeyf0ryourawsaccount/FS4d8Qdva
        certificate: /root/manifests/cert.pem
        private-key: /root/manifests/pk.pem
        user-id: 1234-1234-1234
      s3-region: eu-west-1

* ``guest_additions`` specifies the path to the VirtualBox guest additions ISO
  on the remote machine.
* ``apt_proxy`` sets the configuration for the `apt_proxy plugin <../plugins/apt_proxy>`.
* ``ec2-credentials`` contains all the settings you know from EC2 manifests,
  note that when running `integration tests <../../tests/integration>`__,
  these credentials are also used when running instances.
* ``s3-region`` overrides the s3 bucket region when bootstrapping S3 backed images.
