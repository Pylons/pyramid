import sys
import httplib
import os
import pkg_resources
import shutil
import subprocess
import tempfile
import time
import signal

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
                                      use_distribute=False)
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
            subprocess.check_call(['bin/paster', 'create', '-t', tmpl_name,
                                   'Dingle'])
            os.chdir('Dingle')
            py = os.path.join(self.directory, 'bin', 'python')
            subprocess.check_call([py, 'setup.py', 'install'])
            subprocess.check_call([py, 'setup.py', 'test'])
            paster = os.path.join(self.directory, 'bin', 'paster')
            for ininame, hastoolbar in (('development.ini', True),
                                        ('production.ini', False)):
                proc = subprocess.Popen([paster, 'serve', ininame])
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
                    toolbarchunk = '<div id="pDebug"'
                    if hastoolbar:
                        assert toolbarchunk in data, ininame
                    else:
                        assert not toolbarchunk in data, ininame
                finally:
                    if hasattr(proc, 'terminate'):
                        # 2.6+
                        proc.terminate()
                    else:
                        # 2.5
                        os.kill(proc.pid, signal.SIGTERM)
        finally:
            shutil.rmtree(self.directory)
            os.chdir(self.old_cwd)

if __name__ == '__main__':     # pragma: no cover
    if not hasattr(subprocess, 'check_call'):
        # 2.4
        def check_call(*arg, **kw):
            returncode = subprocess.call(*arg, **kw)
            if returncode:
                raise ValueError(returncode)
        subprocess.check_call = check_call

    templates = ['pyramid_starter', 'pyramid_alchemy', 'pyramid_routesalchemy',]

    if sys.version_info >= (2, 5):
        templates.append('pyramid_zodb')

    for name in templates:
        test = TemplateTest()
        test.install(name)
    
