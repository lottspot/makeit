import os
from unittest import TestCase
from tempfile import mkdtemp
from shutil   import rmtree
from makeit.loader import MakeItLoader

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