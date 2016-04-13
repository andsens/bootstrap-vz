
Commandline switches
====================
As a developer, there are commandline switches available which can
make your life a lot easier.

+ ``--debug``: Enables debug output in the console. This includes output
  from all commands that are invoked during bootstrapping.
+ ``--pause-on-error``: Pauses the execution when an exception occurs
  before rolling back. This allows you to debug by inspecting the volume
  at the time the error occurred.
+ ``--dry-run``: Prevents the ``run()`` function from being called on all
  tasks. This is useful if you want to see whether the task order is
  correct.
