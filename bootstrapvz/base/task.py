

class Task(object):
    """The task class represents a task that can be run.
    It is merely a wrapper for the run function and should never be instantiated.
    """
    # The phase this task is located in.
    phase = None
    # List of tasks that should run before this task is run
    predecessors = []
    # List of tasks that should run after this task has run
    successors = []

    class __metaclass__(type):
        """Metaclass to control how the class is coerced into a string
        """
        def __repr__(cls):
            """
            :return str: The full module path to the Task
            """
            return cls.__module__ + '.' + cls.__name__

        def __str__(cls):
            """
            :return: The full module path to the Task
            :rtype: str
            """
            return repr(cls)

    @classmethod
    def run(cls, info):
        """The run function, all work is done inside this function

        :param BootstrapInformation info: The bootstrap info object.
        """
        pass
