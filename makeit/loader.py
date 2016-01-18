import os
import glob
import inspect
from doit.cmd_base import TaskLoader
from doit.loader import get_module
from doit.task import dict_to_task

INJECT_STRING   = 'task_before'
TASK_STRING     = 'task_'
LEN_TASK_STRING = len(TASK_STRING)

class MakeItLoader(TaskLoader):
    doitcfg = { 'depfile': '.makeitdb' }
    def __init__(self, cfg={}):
        self.cfg        = cfg
        self._injections = {}
    def load_tasks(self, cmd, opt_values, pos_args):
        makeitcfg = self.cfg.get('makeit')
        if not hasattr(makeitcfg, 'get'):
            raise RuntimeError('Configuration must have a [makeit] section')
        mods      = []
        modpath   = makeitcfg.get('path').split(':')
        self.doitcfg.update(self.cfg.get('doit', {}))
        #  Find absolute paths to task modules
        loadpaths = self._search_module_paths(modpath)
        #  Load task generators from modules
        for path in loadpaths:
            mods.append(get_module(path))
        taskgens  = self._collect_taskgens(mods)
        #  Generate task dicts
        taskdicts = self._taskgens_to_dicts(taskgens)
        #  Process makeit extensions out of task dicts
        processed = self._process_makeit_extensions(taskdicts)
        #  Generate Task objects from processed tasks
        return self._processed_dicts_to_tasks(processed), self.doitcfg
    def _search_module_paths(self, paths):
        '''Takes an iterable of director paths
        Searches each directory for python modules
        Returns a list of absolute paths to each module found
        '''
        modpaths = []
        for path in paths:
            if not os.path.isabs(path):
                path = os.path.realpath(path)
            modpaths.extend(glob.glob('%s/*.py' % path))
        return modpaths
    def _collect_taskgens(self, modules):
        '''Takes an iterable of (imported) modules
        Scans each module for task generation methods
        Returns a dictionary of { 'basename': genfunc } pairs of found generators
        '''
        taskgens = {}
        for mod in modules:
            members = dict(inspect.getmembers(mod))
            for name in members.keys():
                val = members[name]
                if callable(val) and name.startswith(TASK_STRING):
                    taskname = name[LEN_TASK_STRING:]
                    taskgens[taskname] = val
        return taskgens
    def _taskgens_to_dicts(self, generators):
        '''Takes an iterable of task generation methods
        Generates tasks, storing each one in a dictionary
        Returns a list of task dictionaries which include makeit extended attributes
        Guarantees that every task will have its 'basename' value set
        '''
        dicts = []
        for taskname in generators.keys():
            generator = generators[taskname]
            if len(inspect.getargspec(generator).args) > 0:
                output = generator(self.cfg)
            else:
                output = generator()
            if hasattr(output, 'next'):     # Generator object
                for task in output:
                    if not task.has_key('basename'):
                        task['basename'] = taskname
                    dicts.append(task)
            else:                           # Assume task dict
                task = output
                if not task.has_key('basename'):
                    task['basename'] = taskname
                dicts.append(task)
        return dicts
    def _process_makeit_extensions(self, dicts):
        '''Process makeit extended attributes in a list of task dicts
        Return a list of task dicts stripped of makeit extended attributes
        '''
        stripped = []
        #  Parse extensions
        for task in dicts:
            task = self._makeit_ext_depinject_parse(task)
            stripped.append(task)
        #  Process extensions
        for task in dicts:
            self._makeit_ext_depinject_do(task)
        return stripped
    def _processed_dicts_to_tasks(self, dicts):
        '''Transform a list of task dicts into a tuple of doit Task objects
        List must first be processed by _process_makeit_extensions
        '''
        tasks = []
        for taskdict in dicts:
            tasks.append(dict_to_task(taskdict))
        return tuple(tasks)
    def _makeit_ext_depinject_parse(self, task):
        '''Stores the dependency injection information for task
        Returns task with INJECT_STRING attribute stripped
        '''
        stripped = {}
        for key in task.keys():
            if key == INJECT_STRING:
                inject_to = task[INJECT_STRING]
                injections = self._injections
                if injections.has_key(inject_to):
                    injections[inject_to].append(task['basename'])
                else:
                    injections[inject_to] = [task['basename']]
            else:
                stripped[key] = task[key]
        return stripped
    def _makeit_ext_depinject_do(self, task):
        '''Inject task_deps to this task which were specified by other tasks'''
        injected_deps = self._injections.get(task['basename'], [])
        if task.has_key('task_dep'):  # task_dep already defined
            task['task_dep'].extend(injected_deps)
        elif len(injected_deps) > 0:  # task_dep not defined, but there are task_dep tasks to add
            task['task_dep'] = injected_deps
        return task
