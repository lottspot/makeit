import os
from unittest import TestCase
from tempfile import mkdtemp
from shutil   import rmtree
from makeit.loader import MakeItLoader
from doit.task import Task

class TestPathSearch(TestCase):
    '''MakeItLoader._search_module_paths
    Should return a list of found python modules
    in the provided search paths
    '''
    def setUp(self):
        self.testdir = mkdtemp()
        self.letters = ['a', 'b', 'c']
        for letter in self.letters:
            basedir = '%s/%s' % (self.testdir, letter)
            modpath = '%s/%s.py' % (basedir, letter)
            os.mkdir(basedir)
            with open(modpath, 'w'):
                pass
    def tearDown(self):
        rmtree(self.testdir)
    def runTest(self):
        loader = MakeItLoader({'makeit': {}})
        expect_files = map(lambda x: '%s/%s/%s.py' % (self.testdir, x, x), self.letters)
        search_paths = map(lambda x: '%s/%s' % (self.testdir, x), self.letters)
        got_files    = loader._search_module_paths(search_paths)
        self.assertListEqual(got_files, expect_files)

class TestCollectTaskgens(TestCase):
    '''MakeItLoader._collect_taskgens
    Should return a dictionary of callable
    members of the passed object
    Assumes TASK_STRING is "task_"
    '''
    def runTest(self):
        class MockModuleA(object):
            def task_a(self):
                return
            def task_b(self):
                return
            def c(self):
                return
        class MockModuleB(object):
            def task_d(self):
                return
            def task_e(self):
                return
            def f(self):
                return
        expect_callables = ['a', 'b', 'd', 'e']
        expect_missing   = ['c', 'f']
        loader = MakeItLoader({'makeit': {}})
        taskgens = loader._collect_taskgens([MockModuleA, MockModuleB])
        for name in expect_callables:
            self.assertTrue(callable(taskgens.get(name)))
        for name in expect_missing:
            self.assertIsNone(taskgens.get(name))

# TODO: Test the generator object path (loader.py, 75-78)
class TestTaskgensToDicts(TestCase):
    def setUp(self):
        self.loader = MakeItLoader({'makeit': {}})
    def test_generator_received_config(self):
        generators = {
            'mytaskgen': lambda cfg: {'found_cfg': True} if cfg.has_key('makeit') else {}
        }
        dicts = self.loader._taskgens_to_dicts(generators)
        for task in dicts:
            self.assertTrue(task.get('found_cfg'))
    def test_basename_is_set(self):
        generators = {
            'betrue': lambda: {'actions': ['/bin/true']}
        }
        dicts = self.loader._taskgens_to_dicts(generators)
        task  = dicts[0]
        name  = task.get('name')
        if name is None:
            name = task.get('basename')
        self.assertEqual('betrue', name)

class TestProcessMakeitExtensions(TestCase):
    def setUp(self):
        self.loader = MakeItLoader({'makeit': {}})
        self.tasks = [
            {
                'name': 'second',
                'actions': ['/bin/true']
            },
            {
                'name': 'first',
                'actions': ['/bin/false'],
                'task_before': 'second'
            }
        ]
        self.processed = self.loader._process_makeit_extensions(self.tasks)
    def test_dependency_was_injected(self):
        found_taskdep = False
        for task in self.processed:
            for dep in task.get('task_dep', []):
              if dep == 'first':
                  found_taskdep = True
        self.assertTrue(found_taskdep)
    def test_makeit_extensions_stripped(self):
        makeit_exts = ['task_before']
        for task in self.processed:
            for attr in task.keys():
                self.assertFalse(attr in makeit_exts, 'Found makeit extension (one of %s) in task: %s' % (makeit_exts, task))

class TestProcessedDictsToTasks(TestCase):
    def setUp(self):
        self.loader = MakeItLoader({'makeit': {}})
        self.dicts  = [
            {'name': 'first',  'actions': []},
            {'name': 'second', 'actions': []}
        ]
        self.tasks  = self.loader._processed_dicts_to_tasks(self.dicts)
    def test_task_objects_created(self):
        for task in self.tasks:
            self.assertTrue(isinstance(task, Task))
    def test_got_tuple(self):
        self.assertTrue(isinstance(self.tasks, tuple))