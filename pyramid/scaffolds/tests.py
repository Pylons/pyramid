import sys
import os
import pkg_resources
import shutil
import subprocess
import tempfile
import time

try:
    import httplib
except ImportError: # pragma: no cover
    import http.client as httplib

from pyramid.compat import PY3

class TemplateTest(object):
    def make_venv(self, directory): # pragma: no cover
        import virtualenv
        import sys
        from virtualenv import Logger
        logger = Logger([(Logger.level_for_integer(2), sys.stdout)])
        virtualenv.logger = logger
        virtualenv.create_environment(directory,
                                      site_packages=False,
                                      clear=False,
                                      unzip_setuptools=True,
                                      use_distribute=PY3)
    def install(self, tmpl_name): # pragma: no cover
        try:
            self.old_cwd = os.getcwd()
            self.directory = tempfile.mkdtemp()
            self.make_venv(self.directory)
            os.chdir(pkg_resources.get_distribution('pyramid').location)
            subprocess.check_call(
                [os.path.join(self.directory, 'bin', 'python'),
                 'setup.py', 'develop'])
            os.chdir(self.directory)
            subprocess.check_call(['bin/pcreate', '-s', tmpl_name, 'Dingle'])
            os.chdir('Dingle')
            py = os.path.join(self.directory, 'bin', 'python')
            subprocess.check_call([py, 'setup.py', 'install'])
            if tmpl_name == 'alchemy':
                populate = os.path.join(self.directory, 'bin',
                                        'populate_Dingle')
                subprocess.check_call([populate, 'development.ini'])
            subprocess.check_call([py, 'setup.py', 'test'])
            pserve = os.path.join(self.directory, 'bin', 'pserve')
            for ininame, hastoolbar in (('development.ini', True),
                                        ('production.ini', False)):
                proc = subprocess.Popen([pserve, ininame])
                try:
                    time.sleep(5)
                    proc.poll()
                    if proc.returncode is not None:
                        raise RuntimeError('%s didnt start' % ininame)
                    conn = httplib.HTTPConnection('localhost:6543')
                    conn.request('GET', '/')
                    resp = conn.getresponse()
                    assert resp.status == 200, ininame
                    data = resp.read()
                    toolbarchunk = b'<div id="pDebug"'
                    if hastoolbar:
                        assert toolbarchunk in data, ininame
                    else:
                        assert not toolbarchunk in data, ininame
                finally:
                    proc.terminate()
        finally:
            shutil.rmtree(self.directory)
            os.chdir(self.old_cwd)

if __name__ == '__main__':     # pragma: no cover
    templates = ['starter', 'alchemy',]

    if sys.version_info >= (2, 6) and sys.version_info < (3, 0):
        templates.append('zodb')

    for name in templates:
        test = TemplateTest()
        test.install(name)
    
