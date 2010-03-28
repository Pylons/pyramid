.. index::
   single: resources

.. _resources_chapter:

Resources
=========

A :term:`resource` is any file contained within a Python
:term:`package` which is *not* a Python source code file.  For
example, each of the following is a resource:

- a :term:`Chameleon` template file contained within a Python package.

- a GIF image file contained within a Python package.

- a CSS file contained within a Python package.

- a JavaScript source file contained within a Python package.

- A directory within a package that does not have an ``__init__.py``
  in it (if it possessed an ``__init__.py`` it would *be* a package).

The use of resources is quite common in most web development projects.
For example, when you create a :mod:`repoze.bfg` application using one
of the available "paster" templates, as described in
:ref:`creating_a_project`, the directory representing the application
contains a Python :term:`package`.  Within that Python package, there
are directories full of files which are resources.  For example, there
is a ``templates`` directory which contains ``.pt`` files, and a
``static`` directory which contains ``.css``, ``.js``, and ``.gif``
files.

.. _understanding_resources:

Understanding Resources
-----------------------

Let's imagine you've created a :mod:`repoze.bfg` application that uses
a :term:`Chameleon` ZPT template via the
:func:`repoze.bfg.chameleon_zpt.render_template_to_response` API.  For
example, the application might address the resource named
``templates/some_template.pt`` using that API within a ``views.py``
file inside a ``myapp`` package:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response
   render_template_to_response('templates/some_template.pt')

"Under the hood", when this API is called, :mod:`repoze.bfg` attempts
to make sense out of the string ``templates/some_template.pt``
provided by the developer.  To do so, it first finds the "current"
package.  The "current" package is the Python package in which the
``views.py`` module which contains this code lives.  This would be the
``myapp`` package, according to our example so far.  By resolving the
current package, :mod:`repoze.bfg` has enough information to locate
the actual template file.  These are the elements it needs:

- The *package name* (``myapp``)

- The *resource name* (``templates/some_template.pt``)

:mod:`repoze.bfg` uses the :term:`pkg_resources` API to resolve the
package name and resource name to an absolute
(operating-system-specific) file name.  It eventually passes this
resolved absolute filesystem path to the Chameleon templating engine,
which then uses it to load, parse, and execute the template file.

Package names often contain dots.  For example, ``repoze.bfg`` is a
package.  Resource names usually look a lot like relative UNIX file
paths.

.. index::
   pair: overriding; resources

.. _overriding_resources_section:

Overriding Resources
--------------------

It can often be useful to override specific resources "from outside" a
given :mod:`repoze.bfg` application.  For example, you may wish to
reuse an existing :mod:`repoze.bfg` application more or less
unchanged.  However, some specific template file owned by the
application might have inappropriate HTML, or some static resource
(such as a logo file or some CSS file) might not be appropriate.  You
*could* just fork the application entirely, but it's often more
convenient to just override the resources that are inappropriate and
reuse the application "as is".  This is particularly true when you
reuse some "core" application over and over again for some set of
customers (such as a CMS application, or some bug tracking
application), and you want to make arbitrary visual modifications to a
particular application deployment without forking the underlying code.

To this end, :mod:`repoze.bfg` contains a feature that makes it
possible to "override" one resource with one or more other resources.
In support of this feature, a :term:`ZCML` directive exists named
``resource``.  The ``resource`` directive allows you to *override* the
following kinds of resources defined in any Python package:

- Individual :term:`Chameleon` templates.

- A directory containing multiple Chameleon templates.

- Individual static files served up by an instance of the
  ``repoze.bfg.view.static`` helper class.

- A directory of static files served up by an instance of the
  ``repoze.bfg.view.static`` helper class.

- Any other resource (or set of resources) addressed by code that uses
  the setuptools :term:`pkg_resources` API.

Usually, overriding a resource in an existing application means
performing the following steps:

- Create a new Python package.  The easiest way to do this is to
  create a new :mod:`repoze.bfg` application using the "paster"
  template mechanism.  See :ref:`creating_a_project` for more
  information.

- Install the new package into the same Python environment as the
  original application (e.g. ``python setup.py develop`` or ``python
  setup.py install``).

- Change the ``configure.zcml`` in the new package to include one or
  more ``resource`` ZCML directives (see :ref:`resource_directive`
  below).  The new package's ``configure.zcml`` should then include
  the original :mod:`repoze.bfg` application's ``configure.zcml`` via
  an include statement, e.g.  ``<include
  package="theoriginalpackage"/>``.

- Add override resources to the package as necessary.

- Change the Paste ``.ini`` file that starts up the original
  application.  Add a ``configure_zcml`` statement within the
  application's section in the file which points at your *new*
  package's ``configure.zcml`` file.  See :ref:`environment_chapter`
  for more information about this setting.

Note that overriding resources is not the only way to extend or modify
the behavior of an existing :mod:`repoze.bfg` application.  A "heavier
hammer" way to do the same thing is explained in
:ref:`extending_chapter`.  The heavier hammer way allows you to
replace a :term:`view` wholesale rather than resources that might be
used by a view.

.. index::
   single: override_resource

.. _override_resource:

The ``override_resource`` API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An individual call to
:meth:`repoze.bfg.configuration.Configurator.override_resource` can
override a single resource.  For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_resource(
            to_override='some.package:templates/mytemplate.pt',
            override_with='another.package:othertemplates/anothertemplate.pt')

The string value passed to both ``to_override`` and ``override_with``
attached to a resource directive is called a "specification".  The
colon separator in a specification separates the *package name* from
the *resource name*.  The colon and the following resource name are
optional.  If they are not specified, the override attempts to resolve
every lookup into a package from the directory of another package.
For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_resource(to_override='some.package',
                            override_with='another.package')

Individual subdirectories within a package can also be overridden:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_resource(to_override='some.package:templates/',
                            override_with='another.package:othertemplates/')


If you wish to override a directory with another directory, you *must*
make sure to attach the slash to the end of both the ``to_override``
specification and the ``override_with`` specification.  If you fail to
attach a slash to the end of a specification that points to a directory,
you will get unexpected results.

You cannot override a directory specification with a file
specification, and vice versa: a startup error will occur if you try.
You cannot override a resource with itself: a startup error will occur
if you try.

Only individual *package* resources may be overridden.  Overrides will
not traverse through subpackages within an overridden package.  This
means that if you want to override resources for both
``some.package:templates``, and ``some.package.views:templates``, you
will need to register two overrides.

The package name in a specification may start with a dot, meaning that
the package is relative to the package in which the configuration
construction file resides (or the ``package`` argument to the
:class:`repoze.bfg.configuration.Configurator` class construction).
For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_resource(to_override='.subpackage:templates/',
                            override_with='another.package:templates/')

Multiple ``override_resource`` statements which name a shared
``to_override`` but a different ``override_with`` specification can be
"stacked" to form a search path.  The first resource that exists in
the search path will be used; if no resource exists in the override
path, the original resource is used.

Resource overrides can actually override resources other than
templates and static files.  Any software which uses the
:func:`pkg_resources.get_resource_filename`,
:func:`pkg_resources.get_resource_stream` or
:func:`pkg_resources.get_resource_string` APIs will obtain an
overridden file when an override is used.

.. index::
   pair: ZCML directive; resource

.. _resource_zcml_directive:

The ``resource`` ZCML Directive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of using
:meth:`repoze.bfg.configuration.Configurator.override_resource` during
:term:`imperative configuration`, an equivalent can be used to perform
all the tasks described above within :term:`ZCML`.  The ZCML
``resource`` tag is a frontend to using ``override_resource``.

An individual :mod:`repoze.bfg` ``resource`` ZCML statement can
override a single resource.  For example:

.. code-block:: xml
   :linenos:

    <resource
      to_override="some.package:templates/mytemplate.pt"
      override_with="another.package:othertemplates/anothertemplate.pt"
    />

The string value passed to both ``to_override`` and ``override_with``
attached to a resource directive is called a "specification".  The
colon separator in a specification separates the *package name* from
the *resource name*.  The colon and the following resource name are
optional.  If they are not specified, the override attempts to resolve
every lookup into a package from the directory of another package.
For example:

.. code-block:: xml
   :linenos:

    <resource
      to_override="some.package"
      override_with="another.package"
     />

Individual subdirectories within a package can also be overridden:

.. code-block:: xml
   :linenos:

    <resource
      to_override="some.package:templates/"
      override_with="another.package:othertemplates/"
     />

If you wish to override a directory with another directory, you *must*
make sure to attach the slash to the end of both the ``to_override``
specification and the ``override_with`` specification.  If you fail to
attach a slash to the end of a specification that points to a directory,
you will get unexpected results.

The package name in a specification may start with a dot, meaning that
the package is relative to the package in which the ZCML file resides.
For example:

.. code-block:: xml
   :linenos:

    <resource
      to_override=".subpackage:templates/"
      override_with="another.package:templates/"
     />

See also :ref:`resource_directive`.
