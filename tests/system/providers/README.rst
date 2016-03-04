System testing providers are implemented on top of the abstraction
that is the testing harness.

Implementation
--------------
At their most basic level all they need to implement is
the ``boot_image()`` function, which, when called, boots the image
that has been bootstrapped. It should yield something the test can use to
ascertain whether the image has been successfully bootstrapped
(i.e. a reference to the bootlog or an object with various functions to
interact with the booted instance). How this is implemented is up to the
individual provider.

A ``prepare_bootstrap()`` function may also be implemented, to ensure that the
bootstrapping process can succeed (i.e. create the AWS S3 into which an image
should be uploaded).

Both functions are generators that yield, so that they may clean up any created
resources, once testing is done (or failed, so remember to wrap ``yield`` in a
``try:.. finally:..``).

Debugging
---------
When developing a system test provider, debugging through multiple
invocations of ``tox`` can be cumbersome. A short test script, which sets
up logging and invokes a specific test can be used instead:


Example:

.. code-block:: python

    #!/usr/bin/env python

    from tests.system.docker_tests import test_stable
    from bootstrapvz.base.main import setup_loggers

    setup_loggers({'--log': '-', '--color': 'default', '--debug': True})
    test_stable()
