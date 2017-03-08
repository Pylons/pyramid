# -*- coding: utf-8 -*-
"""
Tests against full Pyramid projects created from scratch.

Contributed to the Shabti project by Gaël Pasgrimaud and 
subsequently adapted for use with Pyramid.

"""
import os
import sys
import shutil
import unittest
from ConfigParser import ConfigParser
import re

import pkg_resources
import pyramid
from nose import SkipTest
from paste.fixture import TestFileEnvironment

try:
    import sqlalchemy as sa
    SQLAtesting = True
except ImportError:
    SQLAtesting = False

is_jython = sys.platform.startswith('java')

TEST_OUTPUT_DIRNAME = 'output'

for spec in ['PasteScript', 'Paste', 'PasteDeploy', 'pyramid']:
    pkg_resources.require(spec)

template_path = os.path.join(
    os.path.dirname(__file__), 'filestotest').replace('\\','/')

test_environ = os.environ.copy()
test_environ['PASTE_TESTING'] = 'true'

testenv = TestFileEnvironment(
    os.path.join(os.path.dirname(__file__), TEST_OUTPUT_DIRNAME).replace('\\','/'),
    template_path=template_path,
    environ=test_environ)

projenv = None

def _get_script_name(script):
    if sys.platform == 'win32' and not script.lower().endswith('.exe'):
        script += '.exe'
    return script

def svn_repos_setup():
    res = testenv.run(_get_script_name('svnadmin'), 'create', 'REPOS',
                      printresult=False)
    path = testenv.base_path.replace('\\','/').replace(' ','%20')
    base = 'file://'
    if ':' in path:
        base = 'file:///'
    testenv.svn_url = base + path + '/REPOS'
    assert 'REPOS' in res.files_created
    testenv.ignore_paths.append('REPOS')

class TestBase(unittest.TestCase):
    # template id
    template = ''
    # set this to false to not set/test SA stuff
    sqlatesting = True
    # set this to None to not run tests
    copydict = {}
    
    def setUp(self):
        super(TestBase, self).setUp()
        project_name = ' '.join(self.template.split('_'))
        project_name = project_name.title()
        self.project_name = '%sProject' % project_name.replace(' ', '')
        dir_to_clean = os.path.join(os.path.dirname(__file__), TEST_OUTPUT_DIRNAME)
        if not os.path.isdir(dir_to_clean):
            os.makedirs(dir_to_clean)
    
    def tearDown(self):
        super(TestBase, self).tearDown()
        dir_to_clean = os.path.join(os.path.dirname(__file__), TEST_OUTPUT_DIRNAME)
        cov_dir = os.path.join(dir_to_clean, self.project_name)
        main_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        # Scan and move the coverage files
        # for name in os.listdir(cov_dir):
        #     if name.startswith('.coverage.'):
        #         shutil.move(os.path.join(cov_dir, name), main_dir)
        #
        if os.path.isdir(dir_to_clean):
            shutil.rmtree(dir_to_clean)
    
    def paster_create(self, template_engine='mako', overwrite=False):
        global projenv
        paster_args = ['create', 
                       '--verbose', 
                       '--no-interactive']
        if overwrite:
            paster_args.append('-f')
        paster_args.extend(['--template=pyramid_starter',
                            self.project_name,
                            'version=0.0',
                            'sqlalchemy=%s' % self.sqlatesting,
                            'zip_safe=False',
                            'template_engine=%s' % template_engine])
        res = testenv.run(_get_script_name('paster'), *paster_args)
        expect_fn = [self.project_name.lower(), 'development.ini', 
                    'setup.cfg', 'README.txt', 'setup.py']
        for fn in expect_fn:
            fn = os.path.join(self.project_name, fn)
            if not overwrite:
                assert fn in res.files_created.keys()
            assert fn in res.stdout
        
        if not overwrite:
            setup = res.files_created[os.path.join(self.project_name,'setup.py')]
            setup.mustcontain('0.0')
            setup.mustcontain('%s:main' % self.project_name.lower())
            # setup.mustcontain('main = pyramid.util:PyramidInstaller')
            setup.mustcontain("include_package_data=True")
            assert '0.0' in setup
        testenv.run(_get_script_name(sys.executable)+' setup.py -q egg_info',
                    cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'),
                    expect_stderr=True)
        testenv.run(_get_script_name(sys.executable)+' setup.py -q develop',
                    cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'),
                    expect_stderr=True)
        #testenv.run(_get_script_name('svn'), 'commit', '-m', 'Created project', self.project_name)
        # A new environment with a new
        projenv = TestFileEnvironment(
            os.path.join(testenv.base_path, self.project_name).replace('\\','/'),
            start_clear=False,
            template_path=template_path,
            environ=test_environ)
        projenv.environ['PYTHONPATH'] = (
            projenv.environ.get('PYTHONPATH', '') + ':' + projenv.base_path)
        
        projenv.writefile('.coveragerc', frompath='coveragerc')
    
    def paster_pyramid_create(
                self,
                template_engine='mako', overwrite=False,
                template='pyramid'):
        global projenv
        paster_args = ['create',
                       # '--verbose',
                       '--no-interactive']
        if overwrite:
            paster_args.append('-f')
        paster_args.extend(['--template=%s' % template,
                            self.project_name,
                            'version=0.0',
                            'sqlalchemy=%s' % self.sqlatesting,
                            'zip_safe=False',
                            'template_engine=%s' % template_engine])
        res = testenv.run(_get_script_name('paster'), *paster_args)
        expect_fn = [self.project_name.lower(),
                     # 'development.ini',
                     'setup.cfg',
                     'README.txt',
                     'setup.py']
        for fn in expect_fn:
            fn = os.path.join(self.project_name, fn)
            if not overwrite:
                assert fn in res.files_after.keys()
            # assert fn in res.stdout
        
        if not overwrite:
            setup = res.files_after[os.path.join(self.project_name,'setup.py')]
            setup.mustcontain('0.0')
            setup.mustcontain('%s:main' % self.project_name.lower())
            #setup.mustcontain('main = pyramid.util:PyramidInstaller')
            setup.mustcontain("include_package_data=True")
            assert '0.0' in setup
        testenv.run(_get_script_name(sys.executable)+' setup.py -q egg_info',
                    cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'),
                    expect_stderr=True)
        testenv.run(_get_script_name(sys.executable)+' setup.py -q develop',
                    cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'),
                    expect_stderr=True)
        #testenv.run(_get_script_name('svn'), 'commit', '-m', 'Created project', self.project_name)
        # A new environment with a new
        projenv = TestFileEnvironment(
            os.path.join(testenv.base_path, self.project_name).replace('\\','/'),
            start_clear=False,
            template_path=template_path,
            environ=test_environ)
        projenv.environ['PYTHONPATH'] = (
            projenv.environ.get('PYTHONPATH', '') + ':'
            + projenv.base_path)
        projenv.writefile('.coveragerc', frompath='coveragerc')
    
    def _do_proj_test(self, copydict, emptyfiles=None, match_routes_output=None):
        """Given a dict of files, where the key is a filename in filestotest, the value is
        the destination in the new projects dir. emptyfiles is a list of files that should
        be created and empty."""
        # if pyramid.test.pyramidapp:
        #     pyramid.test.pyramidsapp = None
        
        if not emptyfiles:
            emptyfiles = []
        for original, newfile in copydict.iteritems():
            projenv.writefile(newfile, frompath=original)
            newfile = os.path.join(projenv.cwd, newfile)
            parser = ConfigParser()
            parser.read([newfile])
            if parser.has_section('app:main'):
                opt = parser.get('app:main', 'use')
                if opt.endswith('projectname'):
                    opt = opt.replace('projectname', self.project_name)
                    parser.set('app:main', 'use', opt)
                    fd = open(newfile, 'w')
                    parser.write(fd)
                    fd.close()
        for fi in emptyfiles:
            projenv.writefile(fi)
        
        # here_dir = os.getcwd()
        # test_dir = os.path.join(testenv.cwd, self.project_name).replace('\\','/')
        # os.chdir(test_dir)
        # sys.path.append(test_dir)
        # nose.run(argv=['nosetests', '-d', test_dir])
        # sys.path.pop(-1)
        # os.chdir(here_dir)
        
        # res = projenv.run(_get_script_name('nosetests')+' --with-pylons=test.ini -d',
        #                   expect_stderr=True,
        #                   cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'))
        res = projenv.run(_get_script_name('nosetests')+' -q',
                          expect_stderr=True,
                          cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'))
        if match_routes_output:
            res = projenv.run(_get_script_name('paster')+' routes',
                              expect_stderr=False,
                              cwd=os.path.join(testenv.cwd, self.project_name).replace('\\','/'))
            for pattern in match_routes_output:
                assert re.compile(pattern).search(res.stdout)
        # @@FIXME@@ - It just doesn't want to clean up after itself
        import commands
        done = commands.getoutput('rm -rf %s/*' % testenv.cwd)
    
    def do_nosetests(self, copydict={}, emptyfiles=None):
        # if not copydict:
        #     copydict = {'development.ini':'development.ini'}
        self._do_proj_test(copydict, emptyfiles=emptyfiles)
    
    def test_template(self):
        if self.template:
            self.paster_pyramid_create(template=self.template)
            if self.copydict is not None:
                self.do_nosetests(self.copydict.copy())
    



