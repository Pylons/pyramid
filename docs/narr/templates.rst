Templates
=========

A :term:`template` is a usually file on disk which can be used to
render data provided by a :term:`view`, surrounded by more static
information.

Templating With :term:`Chameleon` (:term:`chameleon.zpt`) Page Templates
------------------------------------------------------------------------

Like Zope, :mod:`repoze.bfg` uses Zope Page Templates (:term:`ZPT`) as
its default and best-supported templating language. However,
:mod:`repoze.bfg` uses a different implementation of the :term:`ZPT`
specification than Zope does: the :term:`Chameleon`
:term:`chameleon.zpt` templating engine. This templating engine
complies largely with the `Zope Page Template
<http://wiki.zope.org/ZPT/FrontPage>`_ template specification and is
significantly faster.

.. note:: The language definition documentation for Chameleon
   ZPT-style templates is available from `the Chameleon website
   <http://chameleon.repoze.org>`_.

.. note:: As of version 0.8.0, :mod:`repoze.bfg` no longer supports
   XSL templates "out of the box".  The :mod:`repoze.bfg.xslt` package
   is an add-on which provides XSL template bindings.

.. note:: As of version 0.8.0, :mod:`repoze.bfg` no longer supports
   Genshi-style Chameleon bindings "out of the box".  The
   :mod:`repoze.bfg.chameleon_genshi` package is an add-on which
   provides Chameleon Genshi-style template support.

.. note:: Jinja2 template bindings are available for :mod:`repoze.bfg`
   in the :mod:`repoze.bfg.jinja2` package.

Given that there is a :term:`chameleon.zpt` template named
``foo.pt`` in a directory in your application named ``templates``,
you can render the template from a view like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response
   def sample_view(context, request):
       return render_template_to_response('templates/foo.pt', foo=1, bar=2)

The first argument to ``render_template_to_response`` shown above (and
its sister function ``render_template``, not shown, which just returns
a string body) is the template *path*.  Above, the path
``templates/foo.pt`` is *relative*.  Relative to what, you ask?
Relative to the directory in which the ``views.py`` file which names
it lives, which is usually the :mod:`repoze.bfg` application's
:term:`package` directory.

``render_template_to_response`` always renders a :term:`chameleon.zpt`
template, and always returns a Response object which has a *status
code* of ``200 OK`` and a *content-type* of ``text-html``.  If you
need more control over the status code and content-type, use the
``render_template`` function instead, which also renders a ZPT
template but returns a string instead of a Response.  You can use the
string manually as a response body:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template
   from webob import Response
   def sample_view(context, request):
       result = render_template('templates/foo.pt', foo=1, bar=2)
       response = Response(result)
       response.content_type = 'text/plain'
       return response

:mod:`repoze.bfg` loads the template and keeps it in memory between
requests. This means that modifications to the ZPT require a restart
before you can see the changes.

Using ZPT Macros in :mod:`repoze.bfg`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike Zope 3 "browser views", :mod:`repoze.bfg` doesn't make any
names (such as ``context`` and ``view``) available to
:term:`chameleon.zpt` templates by default.  Instead, it expects you
to pass all the names you need into the template.  One of the common
needs in ZPT-based template is to one template's "macros" from within
a different template.  In Zope, this is typically handled by
retrieving the template from the ``context``.  To do the same thing in
:mod:`repoze.bfg`, you need to make the macro template itself
available to the rendered template by passing the macro template
itself (or even the macro itself) into the rendered template.  To make
a macro available to the rendered template, you can retrieve a
different template using the ``get_template`` API, and pass it in to
the template being rendered.  For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response
   from repoze.bfg.chameleon_zpt import get_template

   def my_view(context, request):
       main = get_template('templates/master.pt')
       return render_template_to_response('templates/mytemplate.pt', main=main)

Where ``templates/master.pt`` might look like so:

.. code-block:: xml
   :linenos:

    <html xmlns="http://www.w3.org/1999/xhtml" 
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal">
       <span tal:define-macro="hello">
          <h1>
             Hello <span metal:define-slot="name">Fred</span>!
          </h1>
       </span>
    </html>

And ``templates/mytemplate.pt`` might look like so:

.. code-block:: xml
   :linenos:

    <html xmlns="http://www.w3.org/1999/xhtml" 
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal">
       <span tal:use-macro="main.macros['hello']">
          <span metal:use-macro="name">
             <span metal:fill-slot="name">Chris</span>
          </span>
       </span>
    </html>

.. _reload_templates_section:

Automatically Reloading Templates
---------------------------------

It's often convenient to see changes you make to a template file
appear immediately without needing to restart the application process.
:mod:`repoze.bfg` allows you configure your application development
environment so that a change to a template will be automatically
detected, and the template will be reloaded on the next rendering.

.. warning:: auto-template-reload behavior is not recommended for
             production sites as it slows rendering; it's usually only
             desirable during development.

In order to turn on automatic reloading of templates, you can use an
environment variable setting or a configuration file setting.

To use an environment variable, start your application under a shell
using the ``BFG_RELOAD_TEMPLATES`` environment variable set to ``1``,
For example::

  $ BFG_RELOAD_TEMPLATES=1 bin/paster serve myproject.ini

To use a setting in the the application ``.ini`` file for the same
purpose, set the ``reload_templates`` key to ``true`` within the
application's configuration section, e.g.::

  [app:main]
  use = egg:MyProject#app
  reload_templates = true

Using Text Templates
--------------------

:mod:`repoze.bfg` also allows for the use of templates which are
composed entirely of non-XML text via :term:`Chameleon`.  To do so,
you can create templates that are entirely composed of text except for
``${name}`` -style substitution points.  The rendering API is a mirror
of the ZPT rendering facility, it's just imported from another place;
see :ref:`template_module` for more information.

Templating with other Templating Languages
------------------------------------------

Because :term:`view` functions are typically the only code in
:mod:`repoze.bfg` that need to know anything about templates, and
because view functions are very simple Python, you can use whatever
templating system you're most comfortable with within
:mod:`repoze.bfg`.  Install the templating system, import its API
functions into your views module, use those APIs to generate a string,
then return that string as the body of a :term:`WebOb` ``Response``
object.  Assuming you have `Mako <http://www.makotemplates.org/>`_
installed, here's an example of using Mako from within a
:mod:`repoze.bfg` :term:`view`:

.. code-block:: python
   :linenos:

   from mako.template import Template
   from webob import Response

   def make_view(context, request):
       template = Template(filename='/templates/template.mak')
       result = template.render(name=context.name)
       response = Response(result)
       return response

.. note:: It's reasonably easy to write custom templating system
   binding packages for use under :mod:`repoze.bfg`.  See
   :ref:`available_template_system_bindings` for example packages.

Note that if you use third-party templating languages, the
auto-template-reload strategy explained in
:ref:`reload_templates_section` will not be available.

.. _available_template_system_bindings:

Available Add-On Template System Bindings
-----------------------------------------

:mod:`repoze.bfg.xslt` is an add-on which provides XSL template
bindings.  It lives in the Repoze Subversion repository at
`http://svn.repoze.org/repoze.bfg.xslt
<http://svn.repoze.org/repoze.bfg.xslt>`_.

:mod:`repoze.bfg.chameleon_genshi` package is an add-on which provides
Chameleon Genshi-style template support.  It lives in the Repoze
Subversion repository at `http://svn.repoze.org/repoze.bfg.chameleon_genshi
<http://svn.repoze.org/repoze.bfg.chameleon_genshi>`_.

Jinja2 template bindings are available for :mod:`repoze.bfg` in the
:mod:`repoze.bfg.jinja2` package.  It lives in the Repoze Subversion
repository at `http://svn.repoze.org/repoze.bfg.jinja2
<http://svn.repoze.org/repoze.bfg.jinja2>`_.

Courtesty of Carlos de la Guardia, bindings for the Zope
``zope.pagetemplate`` package ("old TAL") are available from
`http://svn.repoze.org/repoze.bfg.zopepagetemplate/
<http://svn.repoze.org/repoze.bfg.zopepagetemplate/>`_.

