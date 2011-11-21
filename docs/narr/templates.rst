.. _templates_chapter:

Templates
=========

A :term:`template` is a file on disk which can be used to render
dynamic data provided by a :term:`view`.  :app:`Pyramid` offers a
number of ways to perform templating tasks out of the box, and
provides add-on templating support through a set of bindings packages.

Out of the box, :app:`Pyramid` provides templating via the :term:`Chameleon`
and :term:`Mako` templating libraries. :term:`Chameleon` provides support for
two different types of templates: :term:`ZPT` templates, and text templates.

Before discussing how built-in templates are used in
detail, we'll discuss two ways to render templates within
:app:`Pyramid` in general: directly, and via renderer
configuration.

.. index::
   single: templates used directly

.. _templates_used_directly:

Using Templates Directly
------------------------

The most straightforward way to use a template within
:app:`Pyramid` is to cause it to be rendered directly within a
:term:`view callable`.  You may use whatever API is supplied by a
given templating engine to do so.

:app:`Pyramid` provides various APIs that allow you to render templates
directly from within a view callable.  For example, if there is a
:term:`Chameleon` ZPT template named ``foo.pt`` in a directory  named
``templates`` in your application, you can render the template from
within the body of a view callable like so:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render_to_response

   def sample_view(request):
       return render_to_response('templates/foo.pt', 
                                 {'foo':1, 'bar':2}, 
                                 request=request)

.. warning::

   Earlier iterations of this documentation
   (pre-version-1.3) encouraged the application developer to use
   ZPT-specific APIs such as
   :func:`pyramid.chameleon_zpt.render_template_to_response` and
   :func:`pyramid.chameleon_zpt.render_template` to render templates
   directly.  This style of rendering still works, but at least for
   purposes of this documentation, those functions are deprecated.
   Application developers are encouraged instead to use the functions
   available in the :mod:`pyramid.renderers` module to perform
   rendering tasks.  This set of functions works to render templates
   for all renderer extensions registered with :app:`Pyramid`.

The ``sample_view`` :term:`view callable` function above returns a
:term:`response` object which contains the body of the
``templates/foo.pt`` template.  In this case, the ``templates``
directory should live in the same directory as the module containing
the ``sample_view`` function.  The template author will have the names
``foo`` and ``bar`` available as top-level names for replacement or
comparison purposes.

In the example above, the path ``templates/foo.pt`` is relative to the
directory containing the file which defines the view configuration.
In this case, this is the directory containing the file that
defines the ``sample_view`` function.  Although a renderer path is
usually just a simple relative pathname, a path named as a renderer
can be absolute, starting with a slash on UNIX or a drive letter
prefix on Windows.

.. warning::

   Only :term:`Chameleon` templates support defining a renderer for a
   template relative to the location of the module where the view
   callable is defined.  Mako templates, and other templating system
   bindings work differently.  In particular, Mako templates use a
   "lookup path" as defined by the ``mako.directories`` configuration
   file instead of treating relative paths as relative to the current
   view module.  See :ref:`mako_templates`.

The path can alternately be a :term:`asset specification` in the form
``some.dotted.package_name:relative/path``. This makes it possible to
address template assets which live in another package.  For example:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render_to_response

   def sample_view(request):
       return render_to_response('mypackage:templates/foo.pt',
                                 {'foo':1, 'bar':2},
                                 request=request)

An asset specification points at a file within a Python *package*.
In this case, it points at a file named ``foo.pt`` within the
``templates`` directory of the ``mypackage`` package.  Using a
asset specification instead of a relative template name is usually
a good idea, because calls to ``render_to_response`` using asset
specifications will continue to work properly if you move the code
containing them around.

.. note::

   Mako templating system bindings also respect absolute asset
   specifications as an argument to any of the ``render*`` commands.  If a
   template name defines a ``:`` (colon) character and is not an absolute
   path, it is treated as an absolute asset specification.

In the examples above we pass in a keyword argument named ``request``
representing the current :app:`Pyramid` request. Passing a request
keyword argument will cause the ``render_to_response`` function to
supply the renderer with more correct system values (see
:ref:`renderer_system_values`), because most of the information required
to compose proper system values is present in the request.  If your
template relies on the name ``request`` or ``context``, or if you've
configured special :term:`renderer globals`, make sure to pass
``request`` as a keyword argument in every call to to a
``pyramid.renderers.render_*`` function.

Every view must return a :term:`response` object, except for views
which use a :term:`renderer` named via view configuration (which we'll
see shortly).  The :func:`pyramid.renderers.render_to_response`
function is a shortcut function that actually returns a response
object. This allows the example view above to simply return the result 
of its call to ``render_to_response()`` directly. 

Obviously not all APIs you might call to get response data will return a
response object. For example, you might render one or more templates to
a string that you want to use as response data.  The
:func:`pyramid.renderers.render` API renders a template to a string. We
can manufacture a :term:`response` object directly, and use that string
as the body of the response:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render
   from pyramid.response import Response

   def sample_view(request):
       result = render('mypackage:templates/foo.pt', 
                       {'foo':1, 'bar':2}, 
                       request=request)
       response = Response(result)
       return response

Because :term:`view callable` functions are typically the only code in
:app:`Pyramid` that need to know anything about templates, and because view
functions are very simple Python, you can use whatever templating system you're
most comfortable with within :app:`Pyramid`.  Install the templating system,
import its API functions into your views module, use those APIs to generate a
string, then return that string as the body of a :app:`Pyramid`
:term:`Response` object.

For example, here's an example of using "raw" `Mako
<http://www.makotemplates.org/>`_ from within a :app:`Pyramid` :term:`view`:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from mako.template import Template
   from pyramid.response import Response

   def make_view(request):
       template = Template(filename='/templates/template.mak')
       result = template.render(name=request.params['name'])
       response = Response(result)
       return response

You probably wouldn't use this particular snippet in a project, because it's
easier to use the Mako renderer bindings which already exist in
:app:`Pyramid`. But if your favorite templating system is not supported as a
renderer extension for :app:`Pyramid`, you can create your own simple
combination as shown above.

.. note::

   If you use third-party templating languages without cooperating
   :app:`Pyramid` bindings directly within view callables, the
   auto-template-reload strategy explained in
   :ref:`reload_templates_section` will not be available, nor will the
   template asset overriding capability explained in
   :ref:`overriding_assets_section` be available, nor will it be
   possible to use any template using that language as a
   :term:`renderer`.  However, it's reasonably easy to write custom
   templating system binding packages for use under :app:`Pyramid` so
   that templates written in the language can be used as renderers.
   See :ref:`adding_and_overriding_renderers` for instructions on how
   to create your own template renderer and
   :ref:`available_template_system_bindings` for example packages.

If you need more control over the status code and content-type, or
other response attributes from views that use direct templating, you
may set attributes on the response that influence these values.

Here's an example of changing the content-type and status of the
response object returned by
:func:`~pyramid.renderers.render_to_response`:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render_to_response

   def sample_view(request):
       response = render_to_response('templates/foo.pt',
                                     {'foo':1, 'bar':2},
                                     request=request)
       response.content_type = 'text/plain'
       response.status_int = 204
       return response

Here's an example of manufacturing a response object using the result
of :func:`~pyramid.renderers.render` (a string):

.. code-block:: python
   :linenos:

   from pyramid.renderers import render
   from pyramid.response import Response

   def sample_view(request):
       result = render('mypackage:templates/foo.pt',
                       {'foo':1, 'bar':2}, 
                       request=request)
       response = Response(result)
       response.content_type = 'text/plain'
       return response

.. index::
   single: templates used as renderers
   single: template renderers
   single: renderer (template)


.. index::
   pair: renderer; system values

.. _renderer_system_values:

System Values Used During Rendering
-----------------------------------

When a template is rendered using
:func:`~pyramid.renderers.render_to_response` or
:func:`~pyramid.renderers.render`, the renderer representing the
template will be provided with a number of *system* values.  These
values are provided in a dictionary to the renderer and include:

``context``
  The current :app:`Pyramid` context if ``request`` was provided as
  a keyword argument, or ``None``.

``request``
  The request provided as a keyword argument.

``renderer_name``
  The renderer name used to perform the rendering,
  e.g. ``mypackage:templates/foo.pt``.

``renderer_info`` 
  An object implementing the :class:`pyramid.interfaces.IRendererInfo`
  interface.  Basically, an object with the following attributes:
  ``name``, ``package`` and ``type``.

You can define more values which will be passed to every template
executed as a result of rendering by defining :term:`renderer
globals`.

What any particular renderer does with these system values is up to the
renderer itself, but most template renderers, including Chameleon and
Mako renderers, make these names available as top-level template
variables.

.. index::
   pair: renderer; templates

.. _templates_used_as_renderers:

Templates Used as Renderers via Configuration
---------------------------------------------

An alternative to using :func:`~pyramid.renderers.render_to_response`
to render templates manually in your view callable code, is
to specify the template as a :term:`renderer` in your
*view configuration*. This can be done with any of the 
templating languages supported by :app:`Pyramid`.

To use a renderer via view configuration, specify a template
:term:`asset specification` as the ``renderer`` argument, or
attribute to the :term:`view configuration` of a :term:`view
callable`.  Then return a *dictionary* from that view callable.  The
dictionary items returned by the view callable will be made available
to the renderer template as top-level names.

The association of a template as a renderer for a :term:`view
configuration` makes it possible to replace code within a :term:`view
callable` that handles the rendering of a template.

Here's an example of using a :class:`~pyramid.view.view_config`
decorator to specify a :term:`view configuration` that names a
template renderer:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='templates/foo.pt')
   def my_view(request):
       return {'foo':1, 'bar':2}

.. note:: You do not need to supply the ``request`` value as a key
   in the dictionary result returned from a renderer-configured view
   callable. :app:`Pyramid` automatically supplies this value for
   you so that the "most correct" system values are provided to
   the renderer.

.. warning::

   The ``renderer`` argument to the ``@view_config`` configuration decorator
   shown above is the template *path*.  In the example above, the path
   ``templates/foo.pt`` is *relative*.  Relative to what, you ask?  Because
   we're using a Chameleon renderer, it means "relative to the directory in
   which the file which defines the view configuration lives".  In this case,
   this is the directory containing the file that defines the ``my_view``
   function.  View-configuration-relative asset specifications work only
   in Chameleon, not in Mako templates.

Similar renderer configuration can be done imperatively.  See
:ref:`views_which_use_a_renderer`.  See also :ref:`built_in_renderers`.

Although a renderer path is usually just a simple relative pathname, a path
named as a renderer can be absolute, starting with a slash on UNIX or a drive
letter prefix on Windows.  The path can alternately be an :term:`asset
specification` in the form ``some.dotted.package_name:relative/path``, making
it possible to address template assets which live in another package.

Not just any template from any arbitrary templating system may be used as a
renderer.  Bindings must exist specifically for :app:`Pyramid` to use a
templating language template as a renderer.  Currently, :app:`Pyramid` has
built-in support for two Chameleon templating languages: ZPT and text, and
the Mako templating system.  See :ref:`built_in_renderers` for a discussion
of their details.  :app:`Pyramid` also supports the use of :term:`Jinja2`
templates as renderers.  See :ref:`available_template_system_bindings`.

.. sidebar:: Why Use A Renderer via View Configuration

   Using a renderer in view configuration is usually a better way to
   render templates than using any rendering API directly from within a
   :term:`view callable` because it makes the view callable more
   unit-testable.  Views which use templating or rendering APIs directly
   must return a :term:`Response` object.  Making testing assertions
   about response objects is typically an indirect process, because it
   means that your test code often needs to somehow parse information
   out of the response body (often HTML).  View callables configured
   with renderers externally via view configuration typically return a
   dictionary, as above.  Making assertions about results returned in a
   dictionary is almost always more direct and straightforward than
   needing to parse HTML.

By default, views rendered via a template renderer return a :term:`Response`
object which has a *status code* of ``200 OK``, and a *content-type* of
``text/html``.  To vary attributes of the response of a view that uses a
renderer, such as the content-type, headers, or status attributes, you must
use the API of the :class:`pyramid.response.Response` object exposed as
``request.response`` within the view before returning the dictionary.  See
:ref:`request_response_attr` for more information.

The same set of system values are provided to templates rendered via a
renderer view configuration as those provided to templates rendered
imperatively.  See :ref:`renderer_system_values`.


.. index::
   single: Chameleon ZPT templates
   single: ZPT templates (Chameleon)

.. _chameleon_zpt_templates:

:term:`Chameleon` ZPT Templates
-------------------------------

Like :term:`Zope`, :app:`Pyramid` uses :term:`ZPT` (Zope Page
Templates) as its default templating language.  However,
:app:`Pyramid` uses a different implementation of the :term:`ZPT`
specification than Zope does: the :term:`Chameleon` templating
engine. The Chameleon engine complies largely with the `Zope Page
Template <http://wiki.zope.org/ZPT/FrontPage>`_ template
specification.  However, it is significantly faster.

The language definition documentation for Chameleon ZPT-style
templates is available from `the Chameleon website
<http://chameleon.repoze.org/>`_.

Given a :term:`Chameleon` ZPT template named ``foo.pt`` in a directory
in your application named ``templates``, you can render the template as
a :term:`renderer` like so:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='templates/foo.pt')
   def my_view(request):
       return {'foo':1, 'bar':2}

See also :ref:`built_in_renderers` for more general information about
renderers, including Chameleon ZPT renderers.

.. index::
   single: ZPT template (sample)

A Sample ZPT Template
~~~~~~~~~~~~~~~~~~~~~

Here's what a simple :term:`Chameleon` ZPT template used under
:app:`Pyramid` might look like:

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
	  href="http://docs.pylonsproject.org/projects/pyramid/current/"
         >pyramid</a> web
	  application framework.</h1>
      </body>
    </html>

Note the use of :term:`Genshi` -style ``${replacements}`` above.  This
is one of the ways that :term:`Chameleon` ZPT differs from standard
ZPT.  The above template expects to find a ``project`` key in the set
of keywords passed in to it via :func:`~pyramid.renderers.render` or
:func:`~pyramid.renderers.render_to_response`. Typical ZPT
attribute-based syntax (e.g. ``tal:content`` and ``tal:replace``) also
works in these templates.

.. index::
   single: ZPT macros
   single: Chameleon ZPT macros

Using ZPT Macros in :app:`Pyramid`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a :term:`renderer` is used to render a template, :app:`Pyramid` makes at
least two top-level names available to the template by default: ``context``
and ``request``.  One of the common needs in ZPT-based templates is to use
one template's "macros" from within a different template.  In Zope, this is
typically handled by retrieving the template from the ``context``.  But the
context in :app:`Pyramid` is a :term:`resource` object, and templates cannot
usually be retrieved from resources.  To use macros in :app:`Pyramid`, you
need to make the macro template itself available to the rendered template by
passing the macro template, or even the macro itself, *into* the rendered
template.  To do this you can use the :func:`pyramid.renderers.get_renderer`
API to retrieve the macro template, and pass it into the template being
rendered via the dictionary returned by the view.  For example, using a
:term:`view configuration` via a :class:`~pyramid.view.view_config` decorator
that uses a :term:`renderer`:

.. code-block:: python
   :linenos:

   from pyramid.renderers import get_renderer
   from pyramid.view import view_config

   @view_config(renderer='templates/mytemplate.pt')
   def my_view(request):
       main = get_renderer('templates/master.pt').implementation()
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

:app:`Pyramid` also allows for the use of templates which are
composed entirely of non-XML text via :term:`Chameleon`.  To do so,
you can create templates that are entirely composed of text except for
``${name}`` -style substitution points.

Here's an example usage of a Chameleon text template.  Create a file
on disk named ``mytemplate.txt`` in your project's ``templates``
directory with the following contents:

.. code-block:: text

   Hello, ${name}!

Then in your project's ``views.py`` module, you can create a view
which renders this template:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='templates/mytemplate.txt')
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
should configure it to ignore these files.  Here's the contents of the
author's ``svn propedit svn:ignore .`` in each of my ``templates``
directories.

.. code-block:: text

   *.pt.py
   *.txt.py

Note that I always name my Chameleon ZPT template files with a ``.pt``
extension and my Chameleon text template files with a ``.txt``
extension so that these ``svn:ignore`` patterns work.

.. index::
   pair: debugging; templates

.. _debug_templates_section:

Nicer Exceptions in Chameleon Templates
---------------------------------------

The exceptions raised by Chameleon templates when a rendering fails
are sometimes less than helpful.  :app:`Pyramid` allows you to
configure your application development environment so that exceptions
generated by Chameleon during template compilation and execution will
contain nicer debugging information.

.. warning:: Template-debugging behavior is not recommended for
             production sites as it slows renderings; it's usually
             only desirable during development.

In order to turn on template exception debugging, you can use an
environment variable setting or a configuration file setting.

To use an environment variable, start your application under a shell
using the ``PYRAMID_DEBUG_TEMPLATES`` operating system environment
variable set to ``1``, For example:

.. code-block:: text

  $ PYRAMID_DEBUG_TEMPLATES=1 bin/pserve myproject.ini

To use a setting in the application ``.ini`` file for the same
purpose, set the ``pyramid.debug_templates`` key to ``true`` within
the application's configuration section, e.g.:

.. code-block:: ini
  :linenos:

  [app:main]
  use = egg:MyProject
  pyramid.debug_templates = true

With template debugging off, a :exc:`NameError` exception resulting
from rendering a template with an undefined variable
(e.g. ``${wrong}``) might end like this:

.. code-block:: text

  File "...", in __getitem__
    raise NameError(key)
  NameError: wrong

Note that the exception has no information about which template was
being rendered when the error occured.  But with template debugging
on, an exception resulting from the same problem might end like so:

.. code-block:: text

    RuntimeError: Caught exception rendering template.
     - Expression: ``wrong``
     - Filename:   /home/fred/env/proj/proj/templates/mytemplate.pt
     - Arguments:  renderer_name: proj:templates/mytemplate.pt
                   template: <PageTemplateFile - at 0x1d2ecf0>
                   xincludes: <XIncludes - at 0x1d3a130>
                   request: <Request - at 0x1d2ecd0>
                   project: proj
                   macros: <Macros - at 0x1d3aed0>
                   context: <MyResource None at 0x1d39130>
                   view: <function my_view at 0x1d23570>

    NameError: wrong

The latter tells you which template the error occurred in, as well as
displaying the arguments passed to the template itself.

.. note::

   Turning on ``pyramid.debug_templates`` has the same effect as using the
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
   single: Mako

.. _mako_templates:

Templating With Mako Templates
------------------------------

:term:`Mako` is a templating system written by Mike Bayer.  :app:`Pyramid`
has built-in bindings for the Mako templating system.  The language
definition documentation for Mako templates is available from `the Mako
website <http://www.makotemplates.org/>`_.

To use a Mako template, given a :term:`Mako` template file named ``foo.mak``
in the ``templates`` subdirectory in your application package named
``mypackage``, you can configure the template as a :term:`renderer` like so:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='foo.mak')
   def my_view(request):
       return {'project':'my project'}

For the above view callable to work, the following setting needs to be
present in the application stanza of your configuration's ``ini`` file:

.. code-block:: ini

   mako.directories = mypackage:templates

This lets the Mako templating system know that it should look for templates
in the ``templates`` subdirectory of the ``mypackage`` Python package.  See
:ref:`mako_template_renderer_settings` for more information about the
``mako.directories`` setting and other Mako-related settings that can be
placed into the application's ``ini`` file.

.. index::
   single: Mako template (sample)

A Sample Mako Template
~~~~~~~~~~~~~~~~~~~~~~

Here's what a simple :term:`Mako` template used under :app:`Pyramid` might
look like:

.. code-block:: xml
   :linenos:

    <html>
    <head>
        <title>${project} Application</title>
    </head>
      <body>
         <h1 class="title">Welcome to <code>${project}</code>, an
	  application generated by the <a
	  href="http://docs.pylonsproject.org/projects/pyramid/current/"
         >pyramid</a> web application framework.</h1>
      </body>
    </html>

This template doesn't use any advanced features of Mako, only the
``${}`` replacement syntax for names that are passed in as
:term:`renderer globals`.  See the `the Mako documentation
<http://www.makotemplates.org/>`_ to use more advanced features.

.. index::
   single: automatic reloading of templates
   single: template automatic reload

.. _reload_templates_section:

Automatically Reloading Templates
---------------------------------

It's often convenient to see changes you make to a template file
appear immediately without needing to restart the application process.
:app:`Pyramid` allows you to configure your application development
environment so that a change to a template will be automatically
detected, and the template will be reloaded on the next rendering.

.. warning:: Auto-template-reload behavior is not recommended for
             production sites as it slows rendering slightly; it's
             usually only desirable during development.

In order to turn on automatic reloading of templates, you can use an
environment variable, or a configuration file setting.

To use an environment variable, start your application under a shell
using the ``PYRAMID_RELOAD_TEMPLATES`` operating system environment
variable set to ``1``, For example:

.. code-block:: text

  $ PYRAMID_RELOAD_TEMPLATES=1 bin/pserve myproject.ini

To use a setting in the application ``.ini`` file for the same
purpose, set the ``pyramid.reload_templates`` key to ``true`` within the
application's configuration section, e.g.:

.. code-block:: ini
  :linenos:

  [app:main]
  use = egg:MyProject
  pyramid.reload_templates = true

.. index::
   single: template system bindings
   single: Jinja2

.. _available_template_system_bindings:

Available Add-On Template System Bindings
-----------------------------------------

Jinja2 template bindings are available for :app:`Pyramid` in the
``pyramid_jinja2`` package. You can get the latest release of
this package from the 
`Python package index <http://pypi.python.org/pypi/pyramid_jinja2>`_
(pypi).

