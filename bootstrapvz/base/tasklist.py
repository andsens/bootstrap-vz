"""The tasklist module contains the TaskList class.
"""

from bootstrapvz.common.exceptions import TaskListError
import logging
log = logging.getLogger(__name__)


class TaskList(object):
    """The tasklist class aggregates all tasks that should be run
    and orders them according to their dependencies.
    """

    def __init__(self, tasks):
        self.tasks = tasks
        self.tasks_completed = []

    def run(self, info, dry_run=False):
        """Converts the taskgraph into a list and runs all tasks in that list

        :param dict info: The bootstrap information object
        :param bool dry_run: Whether to actually run the tasks or simply step through them
        """
        # Get a hold of every task we can find, so that we can topologically sort
        # all tasks, rather than just the subset we are going to run.
        # We pass in the modules which the manifest has already loaded in order
        # to support third-party plugins, which are not in the bootstrapvz package
        # and therefore wouldn't be discovered.
        all_tasks = set(get_all_tasks([info.manifest.modules['provider']] + info.manifest.modules['plugins']))
        # Create a list for us to run
        task_list = create_list(self.tasks, all_tasks)
        # Output the tasklist
        log.debug('Tasklist:\n\t' + ('\n\t'.join(map(repr, task_list))))

        for task in task_list:
            # Tasks are not required to have a description
            if hasattr(task, 'description'):
                log.info(task.description)
            else:
                # If there is no description, simply coerce the task into a string and print its name
                log.info('Running ' + str(task))
            if not dry_run:
                # Run the task
                task.run(info)
            # Remember which tasks have been run for later use (e.g. when rolling back, because of an error)
            self.tasks_completed.append(task)


def load_tasks(function, manifest, *args):
    """Calls ``function`` on the provider and all plugins that have been loaded by the manifest.
    Any additional arguments are passed directly to ``function``.
    The function that is called shall accept the taskset as its first argument and the manifest
    as its second argument.

    :param str function: Name of the function to call
    :param Manifest manifest: The manifest
    :param list args: Additional arguments that should be passed to the function that is called
    """
    tasks = set()
    # Call 'function' on the provider
    getattr(manifest.modules['provider'], function)(tasks, manifest, *args)
    for plugin in manifest.modules['plugins']:
        # Plugins are not required to have whatever function we call
        fn = getattr(plugin, function, None)
        if callable(fn):
            fn(tasks, manifest, *args)
    return tasks


def create_list(taskset, all_tasks):
    """Creates a list of all the tasks that should be run.
    """
    from bootstrapvz.common.phases import order
    # Make sure all_tasks is a superset of the resolved taskset
    if not all_tasks >= taskset:
        msg = ('bootstrap-vz generated a list of all available tasks. '
               'That list is not a superset of the tasks required for bootstrapping. '
               'The tasks that were not found are: {tasks} '
               '(This is an error in the code and not the manifest, please report this issue.)'
               .format(tasks=', '.join(map(str, taskset - all_tasks)))
               )
        raise TaskListError(msg)
    # Create a graph over all tasks by creating a map of each tasks successors
    graph = {}
    for task in all_tasks:
        # Do a sanity check first
        check_ordering(task)
        successors = set()
        # Add all successors mentioned in the task
        successors.update(task.successors)
        # Add all tasks that mention this task as a predecessor
        successors.update(filter(lambda succ: task in succ.predecessors, all_tasks))
        # Create a list of phases that succeed the phase of this task
        succeeding_phases = order[order.index(task.phase) + 1:]
        # Add all tasks that occur in above mentioned succeeding phases
        successors.update(filter(lambda succ: succ.phase in succeeding_phases, all_tasks))
        # Map the successors to the task
        graph[task] = successors

    # Use the strongly connected components algorithm to check for cycles in our task graph
    components = strongly_connected_components(graph)
    cycles_found = 0
    for component in components:
        # Node of 1 is also a strongly connected component but hardly a cycle, so we filter them out
        if len(component) > 1:
            cycles_found += 1
            log.debug('Cycle: {list}\n' + (', '.join(map(repr, component))))
    if cycles_found > 0:
        msg = ('{num} cycles were found in the tasklist, '
               'consult the logfile for more information.'.format(num=cycles_found))
        raise TaskListError(msg)

    # Run a topological sort on the graph, returning an ordered list
    sorted_tasks = topological_sort(graph)

    # Filter out any tasks not in the tasklist
    # We want to maintain ordering, so we don't use set intersection
    sorted_tasks = filter(lambda task: task in taskset, sorted_tasks)
    return sorted_tasks


def get_all_tasks(loaded_modules):
    """Gets a list of all task classes in the package

    :return: A list of all tasks in the package
    :rtype: list
    """
    import pkgutil
    import os.path
    import bootstrapvz
    from bootstrapvz.common.tools import rel_path
    module_paths = set([(rel_path(bootstrapvz.__file__, 'common/tasks'), 'bootstrapvz.common.tasks.')])

    for module in loaded_modules:
        module_path = os.path.dirname(module.__file__)
        module_prefix = module.__name__ + '.'
        module_paths.add((module_path, module_prefix))

    providers = rel_path(bootstrapvz.__file__, 'providers')
    for module_loader, module_name, ispkg in pkgutil.iter_modules([providers, 'bootstrapvz.providers']):
        module_path = os.path.join(module_loader.path, module_name)
        # The prefix param seems to do nothing, so we prefix the module name ourselves
        module_prefix = 'bootstrapvz.providers.{}.'.format(module_name)
        module_paths.add((module_path, module_prefix))

    plugins = rel_path(bootstrapvz.__file__, 'plugins')
    for module_loader, module_name, ispkg in pkgutil.iter_modules([plugins, 'bootstrapvz.plugins']):
        module_path = os.path.join(module_loader.path, module_name)
        module_prefix = 'bootstrapvz.plugins.{}.'.format(module_name)
        module_paths.add((module_path, module_prefix))

    # Get generators that return all classes in a module
    generators = []
    for (module_path, module_prefix) in module_paths:
        generators.append(get_all_classes(module_path, module_prefix))
    import itertools
    classes = itertools.chain(*generators)

    # lambda function to check whether a class is a task (excluding the superclass Task)
    def is_task(obj):
        from task import Task
        return issubclass(obj, Task) and obj is not Task
    return filter(is_task, classes)  # Only return classes that are tasks


def get_all_classes(path=None, prefix='', excludes=[]):
    """ Given a path to a package, this function retrieves all the classes in it

    :param str path: Path to the package
    :param str prefix: Name of the package followed by a dot
    :param list excludes: List of str matching module names that should be ignored
    :return: A generator that yields classes
    :rtype: generator
    :raises Exception: If a module cannot be inspected.
    """
    import pkgutil
    import importlib
    import inspect

    def walk_error(module_name):
        if not any(map(lambda excl: module_name.startswith(excl), excludes)):
            raise TaskListError('Unable to inspect module ' + module_name)
    walker = pkgutil.walk_packages([path], prefix, walk_error)
    for _, module_name, _ in walker:
        if any(map(lambda excl: module_name.startswith(excl), excludes)):
            continue
        module = importlib.import_module(module_name)
        classes = inspect.getmembers(module, inspect.isclass)
        for class_name, obj in classes:
            # We only want classes that are defined in the module, and not imported ones
            if obj.__module__ == module_name:
                    yield obj


def check_ordering(task):
    """Checks the ordering of a task in relation to other tasks and their phases.

    This function checks for a subset of what the strongly connected components algorithm does,
    but can deliver a more precise error message, namely that there is a conflict between
    what a task has specified as its predecessors or successors and in which phase it is placed.

    :param Task task: The task to check the ordering for
    :raises TaskListError: If there is a conflict between task precedence and phase precedence
    """
    for successor in task.successors:
        # Run through all successors and throw an error if the phase of the task
        # lies before the phase of a successor, log a warning if it lies after.
        if task.phase > successor.phase:
            msg = ("The task {task} is specified as running before {other}, "
                   "but its phase '{phase}' lies after the phase '{other_phase}'"
                   .format(task=task, other=successor, phase=task.phase, other_phase=successor.phase))
            raise TaskListError(msg)
        if task.phase < successor.phase:
            log.warn("The task {task} is specified as running before {other} "
                     "although its phase '{phase}' already lies before the phase '{other_phase}' "
                     "(or the task has been placed in the wrong phase)"
                     .format(task=task, other=successor, phase=task.phase, other_phase=successor.phase))
    for predecessor in task.predecessors:
        # Run through all successors and throw an error if the phase of the task
        # lies after the phase of a predecessor, log a warning if it lies before.
        if task.phase < predecessor.phase:
            msg = ("The task {task} is specified as running after {other}, "
                   "but its phase '{phase}' lies before the phase '{other_phase}'"
                   .format(task=task, other=predecessor, phase=task.phase, other_phase=predecessor.phase))
            raise TaskListError(msg)
        if task.phase > predecessor.phase:
            log.warn("The task {task} is specified as running after {other} "
                     "although its phase '{phase}' already lies after the phase '{other_phase}' "
                     "(or the task has been placed in the wrong phase)"
                     .format(task=task, other=predecessor, phase=task.phase, other_phase=predecessor.phase))


def strongly_connected_components(graph):
    """Find the strongly connected components in a graph using Tarjan's algorithm.

    Source: http://www.logarithmic.net/pfh-files/blog/01208083168/sort.py

    :param dict graph: mapping of tasks to lists of successor tasks
    :return: List of tuples that are strongly connected comoponents
    :rtype: list
    """

    result = []
    stack = []
    low = {}

    def visit(node):
        if node in low:
            return

        num = len(low)
        low[node] = num
        stack_pos = len(stack)
        stack.append(node)

        for successor in graph[node]:
            visit(successor)
            low[node] = min(low[node], low[successor])

        if num == low[node]:
            component = tuple(stack[stack_pos:])
            del stack[stack_pos:]
            result.append(component)
            for item in component:
                low[item] = len(graph)

    for node in graph:
        visit(node)

    return result


def topological_sort(graph):
    """Runs a topological sort on a graph.

    Source: http://www.logarithmic.net/pfh-files/blog/01208083168/sort.py

    :param dict graph: mapping of tasks to lists of successor tasks
    :return: A list of all tasks in the graph sorted according to ther dependencies
    :rtype: list
    """
    count = {}
    for node in graph:
        count[node] = 0
    for node in graph:
        for successor in graph[node]:
            count[successor] += 1

    ready = [node for node in graph if count[node] == 0]

    result = []
    while ready:
        node = ready.pop(-1)
        result.append(node)

        for successor in graph[node]:
            count[successor] -= 1
            if count[successor] == 0:
                ready.append(successor)

    return result
