# Makeit: A reimagined task loader for doit #

Makeit is an alternative task loader written for the [doit task automator](http://pydoit.org). Makeit includes a CLI script to execute doit tasks loaded via the makeit task loader. Makeit was written to offer greater flexibility in the definition of doit tasks by adding three capabilities to the task definition workflow:

1. Load tasks from multiple python modules. Also allow these modules to have any name and be loaded from any directory.
2. Allow arbitrary data to be passed to tasks by the user, or to be passed to tasks by one another.
3. Allow tasks to declare themselves as being depended on by other tasks.

Doit tasks are fully compatible with makeit, but makeit tasks which make use of makeit's extensions will not function if dropped in to a doit dodo.py file.

## Configuring makeit ##

When using makeit's CLI script, the working directory must contain a `makeit.cfg` file. This file should be a .ini formatted file (or any other format accepted by python's ConfigParser) which, at a minimum, specifies an empty `[makeit]` section. In order for the configuration to be useful, the `[makeit]` section must specify a `path` directive, which specifies a `:` separated list of directories which contain python modules defining makeit tasks. 

Every python module found within any of these directories will be processed for tasks. Like doit tasks, any defined python function whose name is prefixed with `task_` will be called to create tasks.

## Passing data ##

The makeit.cfg will be processed by the makeit CLI script into a dictionary of `{ 'sectionname': { 'directive1': 'value1', 'directive2': 'value2' } }` items.
This dicitonary will then be passed to any task creation methods which accept an argument.

## Injecting Dependencies ##

Task generation functions may return an additional property in task dictionaries when being processed by makeit. Any task dictionary which contains the key `task_before` and a value which names another task will by dynamically added to the `task_dep` array of the task which it names. If the task which it names does not exist, the key will be silently dropped.
