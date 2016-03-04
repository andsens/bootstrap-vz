The testing framework consists of two parts:
The unit tests and the integration tests.

The `unit tests <unit>`__ are responsible for testing individual
parts of bootstrap-vz, while the `integration tests <integration>`__ test
entire manifests by bootstrapping and booting them.

Selecting tests
---------------
To run one specific test suite simply append the module path to tox:

.. code-block:: sh

	$ tox -e unit tests.unit.releases_tests

Specific tests can be selected by appending the function name with a colon
to the modulepath -- to run more than one tests, simply attach more arguments.


.. code-block:: sh

	$ tox -e unit tests.unit.releases_tests:test_lt tests.unit.releases_tests:test_eq
