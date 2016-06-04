#!/usr/bin/python
import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def generate_graph_data():
    import bootstrapvz.common.tasks
    import bootstrapvz.providers
    import bootstrapvz.plugins
    from bootstrapvz.base.tasklist import get_all_tasks
    tasks = get_all_tasks([bootstrapvz.common.tasks, bootstrapvz.providers, bootstrapvz.plugins])

    def distinct(seq):
        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]
    modules = distinct([task.__module__ for task in tasks])
    task_links = []
    task_links.extend([{'source': task,
                        'target': succ,
                        'definer': task,
                        }
                       for task in tasks
                       for succ in task.successors])
    task_links.extend([{'source': pre,
                        'target': task,
                        'definer': task,
                        }
                       for task in tasks
                       for pre in task.predecessors])

    def mk_phase(phase):
        return {'name': phase.name,
                'description': phase.description,
                }

    def mk_module(module):
        return {'name': module,
                }

    from bootstrapvz.common import phases

    def mk_node(task):
        return {'name': task.__name__,
                'module': modules.index(task.__module__),
                'phase': (i for i, phase in enumerate(phases.order) if phase is task.phase).next(),
                }

    def mk_link(link):
        for key in ['source', 'target', 'definer']:
            link[key] = tasks.index(link[key])
        return link

    return {'phases': map(mk_phase, phases.order),
            'modules': map(mk_module, modules),
            'nodes': map(mk_node, tasks),
            'links': map(mk_link, task_links)}


def write_data(data, output_path=None):
    import json
    if output_path is None:
        import sys
        json.dump(data, sys.stdout, indent=4, separators=(',', ': '))
    else:
        with open(output_path, 'w') as output:
            json.dump(data, output)


if __name__ == '__main__' and __package__ is None:
    from docopt import docopt
    usage = """Usage: taskoverview.py [options]

  Options:
    --output <path> output
    -h, --help           show this help
"""
    opts = docopt(usage)

    data = generate_graph_data()
    write_data(data, opts.get('--output', None))
