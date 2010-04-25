Templates
=========

A :term:`template` is a file on disk which can be used to render
dynamic data provided by a :term:`view`.  :mod:`repoze.bfg` offers a
number of ways to perform templating tasks out of the box, and
provides add-on templating support through a set of bindings packages.

Out of the box, :mod:`repoze.bfg` provides templating via the
:term:`Chameleon` templating library.  :term:`Chameleon` provides
support for two different types of templates: :term:`ZPT` templates
and text templates.

Before discussing how built-in templates are used in
detail, we'll discuss two ways to render templates within
:mod:`repoze.bfg` in general: directly, and via renderer
configuration.

.. index::
   single: templates used directly
   single: Mako

.. _templates_used_directly:

Templates Used Directly
-----------------------

The most straightforward way to use a template within
:mod:`repoze.bfg` is to cause it to be rendered directly within a
:term:`view callable`.  You may use whatever API is supplied by a
given templating engine to do so.

:mod:`repoze.bfg` provides various APIs that allow you to render
:term:`Chameleon` templates directly from within a view callable.  For
example, if there is a :term:`Chameleon` ZPT template named ``foo.pt``
in a directory in your application named ``templates``, you can render
the template from within the body of a view callable like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response

   def sample_view(request):
       return render_template_to_response('templates/foo.pt', foo=1, bar=2)

The ``sample_view`` :term:`view callable` above returns a
:term:`response` object which contains the body of the
``template/foo.pt`` template.  The template author will have the names
``foo`` and ``bar`` available as top-level names for replacement or
comparison purposes.

Every view must return a :term:`response` object (except for views
which use a :term:`renderer`, which we'll see shortly).  The
:func:`repoze.bfg.chameleon_zpt.render_template_to_response` function
is a shortcut function that actually returns a response object, but
not all template APIs know about responses.  When you use a template
API that is "response-ignorant" you can also easily render a template
to a string, and construct your own response object as necessary with
the string as the body.

For example, the :func:`repoze.bfg.chameleon_zpt.render_template` API
returns a string.  We can manufacture a :term:`response` object
directly, and use that string as the body of the response:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template
   from webob import Response

   def sample_view(request):
       result = render_template('templates/foo.pt', foo=1, bar=2)
       response = Response(result)
       return response

Because :term:`view callable` functions are typically the only code in
:mod:`repoze.bfg` that need to know anything about templates, and
because view functions are very simple Python, you can use whatever
templating system you're most comfortable with within
:mod:`repoze.bfg`.  Install the templating system, import its API
functions into your views module, use those APIs to generate a string,
then return that string as the body of a :term:`WebOb`
:term:`Response` object.

For example, here's an example of using `Mako
<http://www.makotemplates.org/>`_ from within a :mod:`repoze.bfg`
:term:`view`:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from mako.template import Template
   from webob import Response

   def make_view(request):
       template = Template(filename='/templates/template.mak')
       result = template.render(name=request.params['name'])
       response = Response(result)
       return response

.. note::

   If you use third-party templating languages without cooperating BFG
   bindings directly within view callables, the auto-template-reload
   strategy explained in :ref:`reload_templates_section` will not be
   available, nor will the template resource overriding capability
   explained in :ref:`overriding_resources_section` be available, nor
   will it be possible to use any template using that language as a
   :term:`renderer`.  However, it's reasonably easy to write custom
   templating system binding packages for use under :mod:`repoze.bfg`
   so that templates written in the language can be used as renderers.
   See :ref:`adding_and_overriding_renderers` for instructions on how
   to create your own template renderer and
   :ref:`available_template_system_bindings` for example packages.

If you need more control over the status code and content-type, or
other response attributes from views that use direct templating, you
may set attributes on the response that influence these values.

Here's an example of changing the content-type and status of the
response object returned by
:func:`repoze.bfg.chameleon_zpt.render_template_to_response`:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response

   def sample_view(request):
       response = render_template_to_response('templates/foo.pt', foo=1, bar=2)
       response.content_type = 'text/plain'
       response.status_int = 204
       return response

Here's an example of manufacturing a response object using the result of
:func:`repoze.bfg.chameleon_zpt.render_template` (a string):

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template
   from webob import Response
   def sample_view(request):
       result = render_template('templates/foo.pt', foo=1, bar=2)
       response = Response(result)
       response.content_type = 'text/plain'
       return response

.. index::
   single: templates used as renderers
   single: template renderers
   single: renderer (template)

.. _templates_used_as_renderers:

Templates Used as Renderers
---------------------------

Instead of using templating system APIs within the body of a view
function directly to render a specific template, you may associate a
template written in a supported templating language with a view
indirectly by specifying it as a :term:`renderer`.

To use a renderer, specify a template :term:`resource specification`
as the ``renderer`` argument or attribute to the :term:`view
configuration` of a :term:`view callable`.  Then return a *dictionary*
from that view callable.  The dictionary items returned by the view
callable will be made available to the renderer template as top-level
names.

The association of a template as a renderer for a :term:`view
configuration` makes it possible to replace code within a :term:`view
callable` that handles the rendering of a template.

Here's an example of using a :class:`repoze.bfg.view.bfg_view`
decorator to specify a :term:`view configuration` that names a
template renderer:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/foo.pt')
   def my_view(request):
       return {'foo':1, 'bar':2}

The ``renderer`` argument to the ``@bfg_view`` configuration decorator
shown above is the template *path*.  In the example above, the path
``templates/foo.pt`` is *relative*.  Relative to what, you ask?
Relative to the directory in which the file which defines the view
configuration lives.  In this case, this is the directory containing
the file that defines the ``my_view`` function.

Although a renderer path is usually just a simple relative pathname, a
path named as a renderer can be absolute, starting with a slash on
UNIX or a drive letter prefix on Windows.  The path can alternately be
a :term:`resource specification` in the form
``some.dotted.package_name:relative/path``, making it possible to
address template resources which live in another package.

When a template :term:`renderer` is used to render the result of a
view callable, several names are passed into the template as top-level
names by default, including ``context`` and ``request``.  Similar
renderer configuration can be done imperatively and via :term:`ZCML`.
See :ref:`views_which_use_a_renderer`.  See also
:ref:`built_in_renderers`.

Not just any template from any arbitrary templating system may be used
as a renderer.  Bindings must exist specifically for :mod:`repoze.bfg`
to use a templating language template as a renderer.  Currently,
:mod:`repoze.bfg` has built-in support for two Chameleon templating
languages: ZPT and text.  See :ref:`built_in_renderers` for a
discussion of their details.  :mod:`repoze.bfg` also supports the use
of :term:`Jinja2` templates as renderers.  See
:ref:`available_template_system_bindings`.

.. sidebar:: Why Use A Renderer

   Using a renderer is usually a better way to render templates than
   using any templating API directly from within a :term:`view
   callable` because it makes the view callable more unit-testable.
   Views which use templating APIs directly must return a
   :term:`Response` object.  Making testing assertions about response
   objects is typically an indirect process, because it means that
   your test code often needs to somehow parse information
   out of the response body (often HTML).  View callables which use
   renderers typically return a dictionary, and making assertions
   about the information is almost always more direct than needing to
   parse HTML.  Specifying a renderer from within :term:`ZCML` (as
   opposed to imperatively or via a ``bfg_view`` decorator, or using a
   template directly from within a view callable) also makes it
   possible for someone to modify the template used to render a view
   without needing to fork your code to do so.  See
   :ref:`extending_chapter` for more information.

By default, views rendered via a template renderer return a
:term:`Response` object which has a *status code* of ``200 OK`` and a
*content-type* of ``text/html``.  To vary attributes of the response
of a view that uses a renderer, such as the content-type, headers, or
status attributes, you must set attributes on the *request* object
within the view before returning the dictionary.  See
:ref:`response_request_attrs` for more information.

.. index::
   single: Chameleon ZPT templates
   single: ZPT templates (Chameleon)

.. _chameleon_zpt_templates:

:term:`Chameleon` ZPT Templates
-------------------------------

Like :term:`Zope`, :mod:`repoze.bfg` uses :term:`ZPT` (Zope Page
Templates) as its default templating language.  However,
:mod:`repoze.bfg` uses a different implementation of the :term:`ZPT`
specification than Zope does: the :term:`Chameleon` templating
engine. The Chameleon engine complies largely with the `Zope Page
Template <http://wiki.zope.org/ZPT/FrontPage>`_ template
specification.  However, it is significantly faster.

The language definition documentation for Chameleon ZPT-style
templates is available from `the Chameleon website
<http://chameleon.repoze.org/>`_.

.. warning:: 

   :term:`Chameleon` only works on :term:`CPython` platforms and
   :term:`Google App Engine`.  On :term:`Jython` and other non-CPython
   platforms, you should use ``repoze.bfg.jinja2`` instead.  See
   :ref:`available_template_system_bindings`.

Given that there is a :term:`Chameleon` ZPT template named ``foo.pt``
in a directory in your application named ``templates``, you can render
the template as a :term:`renderer` like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/foo.pt')
   def my_view(request):
       return {'foo':1, 'bar':2}

If you'd rather use templates directly within a view callable (without
the indirection of using a renderer), see :ref:`chameleon_zpt_module`
for the API description.

See also :ref:`built_in_renderers` for more general information about
renderers, including Chameleon ZPT renderers.

.. index::
   single: sample template

A Sample ZPT Template
~~~~~~~~~~~~~~~~~~~~~

Here's what a simple :term:`Chameleon` ZPT template used under
:mod:`repoze.bfg` might look like:

.. code-block:: xml
   :linenos:

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
          xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>${project} Application</title>
    </head>
      <body>
         <h1 class="title">Welcome to <code>${project}</code>, an
	  application generated by the <a
	  href="http://static.repoze.org/bfgdocs">repoze.bfg</a> web
	  application framework.</h1>
      </body>
    </html>

Note the use of :term:`Genshi` -style ``${replacements}`` above.  This
is one of the ways that :term:`Chameleon` ZPT differs from standard
ZPT.  The above template expects to find a ``project`` key in the set
of keywords passed in to it via
:func:`repoze.bfg.chameleon_zpt.render_template` or
:func:`repoze.bfg.render_template_to_response`. Typical ZPT
attribute-based syntax (e.g. ``tal:content`` and ``tal:replace``) also
works in these templates.

.. index::
   single: ZPT macros
   single: Chameleon ZPT macros

Using ZPT Macros in :mod:`repoze.bfg`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a :term:`renderer` is used to render a template,
:mod:`repoze.bfg` makes at least two top-level names available to the
template by default: ``context`` and ``request``.  One of the common
needs in ZPT-based templates is to use one template's "macros" from within
a different template.  In Zope, this is typically handled by
retrieving the template from the ``context``.  But having a hold of
the context in :mod:`repoze.bfg` is not helpful: templates cannot
usually be retrieved from models.  To use macros in :mod:`repoze.bfg`,
you need to make the macro template itself available to the rendered
template by passing the template in which the macro is defined (or even
the macro itself) *into* the rendered template.  To make a macro
available to the rendered template, you can retrieve a different
template using the :func:`repoze.bfg.chameleon_zpt.get_template` API,
and pass it in to the template being rendered.  For example, using a
:term:`view configuration` via a :class:`repoze.bfg.view.bfg_view`
decorator that uses a :term:`renderer`:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import get_template
   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/mytemplate.pt')
   def my_view(request):
       main = get_template('templates/master.pt')
       return {'main':main}

Where ``templates/master.pt`` might look like so:

.. code-block:: xml
   :linenos:

    <html xmlns="http://www.w3.org/1999/xhtml" 
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal">
      <span metal:define-macro="hello">
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
      <span metal:use-macro="main.macros['hello']">
        <span metal:fill-slot="name">Chris</span>
      </span>
    </html>

.. index::
   single: Chameleon text templates

.. _chameleon_text_templates:

Templating with :term:`Chameleon` Text Templates
------------------------------------------------

:mod:`repoze.bfg` also allows for the use of templates which are
composed entirely of non-XML text via :term:`Chameleon`.  To do so,
you can create templates that are entirely composed of text except for
``${name}`` -style substitution points.

Here's an example usage of a Chameleon text template.  Create a file
on disk named ``mytemplate.txt`` in your project's ``templates``
directory with the following contents::

   Hello, ${name}!

Then in your project's ``views.py`` module, you can create a view
which renders this template:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import get_template
   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/mytemplate.txt')
   def my_view(request):
       return {'name':'world'}

When the template is rendered, it will show:

.. code-block:: text

   Hello, world!

If you'd rather use templates directly within a view callable (without
the indirection of using a renderer), see :ref:`chameleon_text_module`
for the API description.

See also :ref:`built_in_renderers` for more general information about
renderers, including Chameleon text renderers.

.. index::
   single: template renderer side effects

Side Effects of Rendering a Chameleon Template
----------------------------------------------

When a Chameleon template is rendered from a file, the templating
engine writes a file in the same directory as the template file itself
as a kind of cache, in order to do less work the next time the
template needs to be read from disk. If you see "strange" ``.py``
files showing up in your ``templates`` directory (or otherwise
directly "next" to your templates), it is due to this feature.

If you're using a version control system such as Subversion, you
should cause it to ignore these files.  Here's the contents of the
author's ``svn propedit svn:ignore .`` in each of my ``templates``
directories.

.. code-block:: bash
   :linenos:

   *.pt.py
   *.txt.py

Note that I always name my Chameleon ZPT template files with a ``.pt``
extension and my Chameleon text template files with a ``.txt``
extension so that these ``svn:ignore`` patterns work.

.. index::
   single: automatic reloading of templates
   single: template automatic reload

.. _reload_templates_section:

Automatically Reloading Templates
---------------------------------

It's often convenient to see changes you make to a template file
appear immediately without needing to restart the application process.
:mod:`repoze.bfg` allows you to configure your application development
environment so that a change to a template will be automatically
detected, and the template will be reloaded on the next rendering.

.. warning:: auto-template-reload behavior is not recommended for
             production sites as it slows rendering slightly; it's
             usually only desirable during development.

In order to turn on automatic reloading of templates, you can use an
environment variable setting or a configuration file setting.

To use an environment variable, start your application under a shell
using the ``BFG_RELOAD_TEMPLATES`` operating system environment
variable set to ``1``, For example::

  $ BFG_RELOAD_TEMPLATES=1 bin/paster serve myproject.ini

To use a setting in the application ``.ini`` file for the same
purpose, set the ``reload_templates`` key to ``true`` within the
application's configuration section, e.g.::

  [app:main]
  use = egg:MyProject#app
  reload_templates = true

.. _debug_templates_section:

Nicer Exceptions in Templates
-----------------------------

The exceptions raised by Chameleon templates when a rendering fails
are sometimes less than helpful.  :mod:`repoze.bfg` allows you to
configure your application development environment so that exceptions
generated by Chameleon during template compilation and execution will
contain nicer debugging information.

.. warning:: template-debugging behavior is not recommended for
             production sites as it slows renderings; it's usually
             only desirable during development.

In order to turn on template exception debugging, you can use an
environment variable setting or a configuration file setting.

To use an environment variable, start your application under a shell
using the ``BFG_DEBUG_TEMPLATES`` operating system environment
variable set to ``1``, For example::

  $ BFG_DEBUG_TEMPLATES=1 bin/paster serve myproject.ini

To use a setting in the application ``.ini`` file for the same
purpose, set the ``debug_templates`` key to ``true`` within the
application's configuration section, e.g.::

  [app:main]
  use = egg:MyProject#app
  debug_templates = true

With template debugging off, a :exc:`NameError` exception resulting
from rendering a template with an undefined variable
(e.g. ``${wrong}``) might end like this::

  File "/home/fred/env/lib/python2.5/site-packages/Chameleon-1.2.3-py2.5.egg/chameleon/core/utils.py", line 332, in __getitem__
    raise NameError(key)
  NameError: wrong

Note that the exception has no information about which template was
being rendered when the error occured.  But with template debugging
on, an exception resulting from the same problem might end like so::

    RuntimeError: Caught exception rendering template.
     - Expression: ``wrong``
     - Filename:   /home/fred/env/bfgzodb/bfgzodb/templates/mytemplate.pt
     - Arguments:  renderer_name: bfgzodb:templates/mytemplate.pt
                   template: <PageTemplateFile - at 0x1d2ecf0>
                   xincludes: <XIncludes - at 0x1d3a130>
                   request: <Request - at 0x1d2ecd0>
                   project: bfgzodb
                   macros: <Macros - at 0x1d3aed0>
                   context: <MyModel None at 0x1d39130>
                   view: <function my_view at 0x1d23570>

    NameError: wrong

The latter tells you which template the error occurred in, as well as
displaying the arguments passed to the template itself.

.. note::

   Turning on ``debug_templates`` has the same effect as using the
   Chameleon environment variable ``CHAMELEON_DEBUG``.  See `Chameleon
   Environment Variables
   <http://chameleon.repoze.org/docs/latest/config.html#environment-variables>`_
   for more information.

.. index::
   single: template internationalization
   single: internationalization (of templates)

:term:`Chameleon` Template Internationalization
-----------------------------------------------

See :ref:`chameleon_translation_strings` for information about
supporting internationalized units of text within :term:`Chameleon`
templates.

.. index::
   single: template system bindings
   single: Jinja2

.. _available_template_system_bindings:

Available Add-On Template System Bindings
-----------------------------------------

Jinja2 template bindings are available for :mod:`repoze.bfg` in the
``repoze.bfg.jinja2`` package.  It lives in the Repoze Subversion
repository at `http://svn.repoze.org/repoze.bfg.jinja2
<http://svn.repoze.org/repoze.bfg.jinja2>`_; it is also available from
:term:`PyPI`.

