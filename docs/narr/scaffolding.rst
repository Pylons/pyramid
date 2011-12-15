.. _scaffolding_chapter:

Creating Pyramid Scaffolds
==========================

You can extend Pyramid by creating a :term:`scaffold` template.  A scaffold
template is useful if you'd like to distribute a customizable configuration
of Pyramid to other users.  Once you've created a scaffold, and someone has
installed the distribution that houses the scaffold, they can use the
``pcreate`` script to create a custom version of your scaffold's template.
Pyramid itself uses scaffolds to allow people to bootstrap new projects.  For
example, ``pcreate -s alchemy MyStuff`` causes Pyramid to render the
``alchemy`` scaffold template to the ``MyStuff`` directory.

Basics
------

A scaffold template is just a bunch of source files and directories on disk.
A small definition class points at this directory; it is in turn pointed at
by a :term:`setuptools` "entry point" which registers the scaffold so it can
be found by the ``pcreate`` command.

To create a scaffold template, create a Python :term:`distribution` to house
the scaffold which includes a ``setup.py`` that relies on the ``setuptools``
package.  See `Creating a Package
<http://guide.python-distribute.org/creation.html>`_ for more information
about how to do this.  For the sake of example, we'll pretend the
distribution you create is named ``CoolExtension``, and it has a package
directory within it named ``coolextension``

Once you've created the distribution put a "scaffolds" directory within your
distribution's package directory, and create a file within that directory
named ``__init__.py`` with something like the following:

.. code-block:: python
   :linenos:

   # CoolExtension/coolextension/scaffolds/__init__.py

   from pyramid.scaffolds import PyramidTemplate

     class CoolExtensionTemplate(PyramidTemplate):
         _template_dir = 'coolextension_scaffold'
         summary = 'My cool extension'

Once this is done, within the ``scaffolds`` directory, create a template
directory.  Our example used a template directory named
``coolextension_scaffold``.

As you create files and directories within the template directory, note that:

- Files which have a name which are suffixed with the value ``_tmpl`` will be
  rendered, and replacing any instance of the literal string ``{{var}}`` with
  the string value of the variable named ``var`` provided to the scaffold.

- Files and directories with filenames that contain the string ``+var+`` will
  have that string replaced with the value of the ``var`` variable provided
  to the scaffold.

Otherwise, files and directories which live in the template directory will be
copied directly without modification to the ``pcreate`` output location.

The variables provided by the default ``PyramidTemplate`` include ``project``
(the project name provided by the user as an argument to ``pcreate``),
``package`` (a lowercasing and normalizing of the project name provided by
the user), ``random_string`` (a long random string), and ``package_logger``
(the name of the package's logger).

See Pyramid's "scaffolds" package
(https://github.com/Pylons/pyramid/tree/master/pyramid/scaffolds) for
concrete examples of scaffold directories (``zodb``, ``alchemy``, and
``starter``, for example).

After you've created the template directory, add the following to the
``entry_points`` value of your distribution's ``setup.py``:

      [pyramid.scaffold]
      coolextension=coolextension.scaffolds:CoolExtensionTemplate

For example::

    def setup(
          ...,
          entry_points = """\
            [pyramid.scaffold]
            coolextension=coolextension.scaffolds:CoolExtensionTemplate
          """
         )

Run your distribution's ``setup.py develop`` or ``setup.py install``
command. After that, you should be able to see your scaffolding template
listed when you run ``pcreate -l``.  It will be named ``coolextension``
because that's the name we gave it in the entry point setup.  Running
``pcreate -s coolextension MyStuff`` will then render your scaffold to an
output directory named ``MyStuff``.

See the module documentation for :mod:`pyramid.scaffolds` for information
about the API of the :class:`pyramid.scaffolds.PyramidScaffold` class and
related classes.  You can override methods of this class to get special
behavior.

Supporting Older Pyramid Versions
---------------------------------

Because different versions of Pyramid handled scaffolding differently, if you
want to have extension scaffolds that can work across Pyramid 1.0.X, 1.1.X,
1.2.X and 1.3.X, you'll need to use something like this bit of horror while
defining your scaffold template:

.. code-block:: python
   :linenos:

     try: # pyramid 1.0.X
         # "pyramid.paster.paste_script..." doesn't exist past 1.0.X
         from pyramid.paster import paste_script_template_renderer
         from pyramid.paster import PyramidTemplate
     except ImportError:
         try: # pyramid 1.1.X, 1.2.X
             # trying to import "paste_script_template_renderer" fails on 1.3.X
             from pyramid.scaffolds import paste_script_template_renderer
             from pyramid.scaffolds import PyramidTemplate
         except ImportError: # pyramid >=1.3a2
             paste_script_template_renderer = None
             from pyramid.scaffolds import PyramidTemplate

     class CoolExtensionTemplateTemplate(PyramidTemplate):
         _template_dir = 'coolextension_scaffold'
         summary = 'My cool extension'
         template_renderer = staticmethod(paste_script_template_renderer)

And then in the setup.py of the package that contains your scaffold, define
the template as a target of both ``paste.paster_create_template`` (for
``paster create``) and ``pyramid.scaffold`` (for ``pcreate``)::

      [paste.paster_create_template]
      coolextension=coolextension.scaffolds:CoolExtensionTemplate
      [pyramid.scaffold]
      coolextension=coolextension.scaffolds:CoolExtensionTemplate

Doing this hideousness will allow your scaffold to work as a ``paster
create`` target (under 1.0, 1.1, or 1.2) or as a ``pcreate`` target (under
1.3).  If an invoker tries to run ``paster create`` against a scaffold
defined this way under 1.3, an error is raised instructing them to use
``pcreate`` instead.

If you want only to support Pyramid 1.3 only, it's much cleaner, and the API
is stable:

.. code-block:: python
   :linenos:

   from pyramid.scaffolds import PyramidTemplate

   class CoolExtensionTemplate(PyramidTemplate):
       _template_dir = 'coolextension_scaffold'
       summary = 'My cool_extension'

You only need to specify a ``paste.paster_create_template`` entry point
target in your ``setup.py`` if you want your scaffold to be consumable by
users of Pyramid 1.0, 1.1, or 1.2.  To support only 1.3, specifying only the
``pyramid.scaffold`` entry point is good enough.  If you want to support both
``paster create`` and ``pcreate`` (meaning you want to support Pyramid 1.2
and some older version), you'll need to define both.

Examples
--------

Existing third-party distributions which house scaffolding are available via
:term:`PyPI`.  The ``pyramid_jqm``, ``pyramid_zcml`` and ``pyramid_jinja2``
packages house scaffolds.  You can install and examine these packages to see
how they work in the quest to develop your own scaffolding.
