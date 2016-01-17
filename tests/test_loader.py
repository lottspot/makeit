import os
from unittest import TestCase
from tempfile import mkdtemp
from shutil   import rmtree
from makeit.loader import MakeItLoader

class PathSearchTest(TestCase):
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


