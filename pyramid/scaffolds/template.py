# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org) Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import re
import sys
import os

from pyramid.compat import (
    native_,
    bytes_,
    )

from pyramid.scaffolds import copydir

fsenc = sys.getfilesystemencoding()

class Template(object):
    copydir = copydir # for testing
    _template_dir = None

    def __init__(self, name):
        self.name = name

    def template_renderer(self, content, vars, filename=None):
        content = native_(content, fsenc)
        try:
            return bytes_(
                substitute_double_braces(content, TypeMapper(vars)), fsenc)
        except Exception as e:
            _add_except(e, ' in file %s' % filename)
            raise

    def module_dir(self):
        """Returns the module directory of this template."""
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    def template_dir(self):
        assert self._template_dir is not None, (
            "Template %r didn't set _template_dir" % self)
        if isinstance( self._template_dir, tuple):
            return self._template_dir
        else:
            return os.path.join(self.module_dir(), self._template_dir)

    def run(self, command, output_dir, vars):
        self.pre(command, output_dir, vars)
        self.write_files(command, output_dir, vars)
        self.post(command, output_dir, vars)

    def pre(self, command, output_dir, vars): # pragma: no cover
        """
        Called before template is applied.
        """
        pass

    def post(self, command, output_dir, vars): # pragma: no cover
        """
        Called after template is applied.
        """
        pass

    def write_files(self, command, output_dir, vars):
        template_dir = self.template_dir()
        if not self.exists(output_dir):
            self.out("Creating directory %s" % output_dir)
            if not command.simulate:
                # Don't let copydir create this top-level directory,
                # since copydir will svn add it sometimes:
                self.makedirs(output_dir)
        self.copydir.copy_dir(
            template_dir,
            output_dir,
            vars,
            verbosity=command.verbose,
            simulate=command.options.simulate,
            interactive=command.interactive,
            overwrite=command.options.overwrite,
            indent=1,
            template_renderer=self.template_renderer
            )

    def makedirs(self, dir): # pragma: no cover
        return os.makedirs(dir)

    def exists(self, path): # pragma: no cover
        return os.path.exists(path)

    def out(self, msg): # pragma: no cover
        print(msg)

class TypeMapper(dict):

    def __getitem__(self, item):
        options = item.split('|')
        for op in options[:-1]:
            try:
                value = eval_with_catch(op, dict(self.items()))
                break
            except (NameError, KeyError):
                pass
        else:
            value = eval(options[-1], dict(self.items()))
        if value is None:
            return ''
        else:
            return str(value)

def eval_with_catch(expr, vars):
    try:
        return eval(expr, vars)
    except Exception as e:
        _add_except(e, 'in expression %r' % expr)
        raise

double_brace_pattern = re.compile(r'{{(?P<braced>.*?)}}')

def substitute_double_braces(content, values):
    def double_bracerepl(match):
        value = match.group('braced').strip()
        return values[value]
    return double_brace_pattern.sub(double_bracerepl, content)
    
def _add_except(exc, info): # pragma: no cover
    if not hasattr(exc, 'args') or exc.args is None:
        return
    args = list(exc.args)
    if args:
        args[0] += ' ' + info
    else:
        args = [info]
    exc.args = tuple(args)
    return


