.. _templates_chapter:

Templates
=========

A :term:`template` is a file on disk which can be used to render dynamic data
provided by a :term:`view`.  :app:`Pyramid` offers a number of ways to perform
templating tasks out of the box, and provides add-on templating support through
a set of bindings packages.

Before discussing how built-in templates are used in detail, we'll discuss two
ways to render templates within :app:`Pyramid` in general: directly and via
renderer configuration.

.. index::
   single: templates used directly

.. _templates_used_directly:

Using Templates Directly
------------------------

The most straightforward way to use a template within :app:`Pyramid` is to
cause it to be rendered directly within a :term:`view callable`.  You may use
whatever API is supplied by a given templating engine to do so.

:app:`Pyramid` provides various APIs that allow you to render templates directly
from within a view callable.  For example, if there is a :term:`Chameleon` ZPT
template named ``foo.pt`` in a directory named ``templates`` in your
application, you can render the template from within the body of a view
callable like so:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render_to_response

   def sample_view(request):
       return render_to_response('templates/foo.pt',
                                 {'foo':1, 'bar':2},
                                 request=request)

The ``sample_view`` :term:`view callable` function above returns a
:term:`response` object which contains the body of the ``templates/foo.pt``
template.  In this case, the ``templates`` directory should live in the same
directory as the module containing the ``sample_view`` function.  The template
author will have the names ``foo`` and ``bar`` available as top-level names for
replacement or comparison purposes.

In the example above, the path ``templates/foo.pt`` is relative to the
directory containing the file which defines the view configuration. In this
case, this is the directory containing the file that defines the
``sample_view`` function.  Although a renderer path is usually just a simple
relative pathname, a path named as a renderer can be absolute, starting with a
slash on UNIX or a drive letter prefix on Windows. The path can alternatively
be an :term:`asset specification` in the form
``some.dotted.package_name:relative/path``. This makes it possible to address
template assets which live in another package.  For example:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render_to_response

   def sample_view(request):
       return render_to_response('mypackage:templates/foo.pt',
                                 {'foo':1, 'bar':2},
                                 request=request)

An asset specification points at a file within a Python *package*. In this
case, it points at a file named ``foo.pt`` within the ``templates`` directory
of the ``mypackage`` package.  Using an asset specification instead of a
relative template name is usually a good idea, because calls to
:func:`~pyramid.renderers.render_to_response` using asset specifications will
continue to work properly if you move the code containing them to another
location.

In the examples above we pass in a keyword argument named ``request``
representing the current :app:`Pyramid` request. Passing a request keyword
argument will cause the ``render_to_response`` function to supply the renderer
with more correct system values (see :ref:`renderer_system_values`), because
most of the information required to compose proper system values is present in
the request.  If your template relies on the name ``request`` or ``context``,
or if you've configured special :term:`renderer globals`, make sure to pass
``request`` as a keyword argument in every call to a
``pyramid.renderers.render_*`` function.

Every view must return a :term:`response` object, except for views which use a
:term:`renderer` named via view configuration (which we'll see shortly).  The
:func:`pyramid.renderers.render_to_response` function is a shortcut function
that actually returns a response object. This allows the example view above to
simply return the result of its call to ``render_to_response()`` directly.

Obviously not all APIs you might call to get response data will return a
response object. For example, you might render one or more templates to a
string that you want to use as response data.  The
:func:`pyramid.renderers.render` API renders a template to a string. We can
manufacture a :term:`response` object directly, and use that string as the body
of the response:

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
functions are very simple Python, you can use whatever templating system with
which you're most comfortable within :app:`Pyramid`.  Install the templating
system, import its API functions into your views module, use those APIs to
generate a string, then return that string as the body of a :app:`Pyramid`
:term:`Response` object.

For example, here's an example of using "raw" Mako_ from within a
:app:`Pyramid` :term:`view`:

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
easier to use the supported :ref:`Mako bindings
<available_template_system_bindings>`. But if your favorite templating system
is not supported as a renderer extension for :app:`Pyramid`, you can create
your own simple combination as shown above.

.. note::

   If you use third-party templating languages without cooperating
   :app:`Pyramid` bindings directly within view callables, the
   auto-template-reload strategy explained in :ref:`reload_templates_section`
   will not be available, nor will the template asset overriding capability
   explained in :ref:`overriding_assets_section` be available, nor will it be
   possible to use any template using that language as a :term:`renderer`.
   However, it's reasonably easy to write custom templating system binding
   packages for use under :app:`Pyramid` so that templates written in the
   language can be used as renderers. See
   :ref:`adding_and_overriding_renderers` for instructions on how to create
   your own template renderer and :ref:`available_template_system_bindings`
   for example packages.

If you need more control over the status code and content-type, or other
response attributes from views that use direct templating, you may set
attributes on the response that influence these values.

Here's an example of changing the content-type and status of the response
object returned by :func:`~pyramid.renderers.render_to_response`:

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

Here's an example of manufacturing a response object using the result of
:func:`~pyramid.renderers.render` (a string):

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

When a template is rendered using :func:`~pyramid.renderers.render_to_response`
or :func:`~pyramid.renderers.render`, or a ``renderer=`` argument to view
configuration (see :ref:`templates_used_as_renderers`), the renderer
representing the template will be provided with a number of *system* values.
These values are provided to the template:

``request``
  The value provided as the ``request`` keyword argument to
  ``render_to_response`` or ``render`` *or* the request object passed to the
  view when the ``renderer=`` argument to view configuration is being used to
  render the template.

``req``
  An alias for ``request``.

``context``
  The current :app:`Pyramid` :term:`context` if ``request`` was provided as a
  keyword argument to ``render_to_response`` or ``render``, or ``None`` if the
  ``request`` keyword argument was not provided.  This value will always be
  provided if the template is rendered as the result of a ``renderer=``
  argument to the view configuration being used.

``renderer_name``
  The renderer name used to perform the rendering, e.g.,
  ``mypackage:templates/foo.pt``.

``renderer_info``
  An object implementing the :class:`pyramid.interfaces.IRendererInfo`
  interface.  Basically, an object with the following attributes: ``name``,
  ``package``, and ``type``.

``view``
  The view callable object that was used to render this template.  If the view
  callable is a method of a class-based view, this will be an instance of the
  class that the method was defined on.  If the view callable is a function or
  instance, it will be that function or instance.  Note that this value will
  only be automatically present when a template is rendered as a result of a
  ``renderer=`` argument; it will be ``None`` when the ``render_to_response``
  or ``render`` APIs are used.

You can define more values which will be passed to every template executed as a
result of rendering by defining :term:`renderer globals`.

What any particular renderer does with these system values is up to the
renderer itself, but most template renderers make these names available as
top-level template variables.

.. index::
   pair: renderer; templates

.. _templates_used_as_renderers:

Templates Used as Renderers via Configuration
---------------------------------------------

An alternative to using :func:`~pyramid.renderers.render_to_response` to render
templates manually in your view callable code is to specify the template as a
:term:`renderer` in your *view configuration*. This can be done with any of the
templating languages supported by :app:`Pyramid`.

To use a renderer via view configuration, specify a template :term:`asset
specification` as the ``renderer`` argument, or attribute to the :term:`view
configuration` of a :term:`view callable`.  Then return a *dictionary* from
that view callable.  The dictionary items returned by the view callable will be
made available to the renderer template as top-level names.

The association of a template as a renderer for a :term:`view configuration`
makes it possible to replace code within a :term:`view callable` that handles
the rendering of a template.

Here's an example of using a :class:`~pyramid.view.view_config` decorator to
specify a :term:`view configuration` that names a template renderer:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='templates/foo.pt')
   def my_view(request):
       return {'foo':1, 'bar':2}

.. note::

   You do not need to supply the ``request`` value as a key in the dictionary
   result returned from a renderer-configured view callable. :app:`Pyramid`
   automatically supplies this value for you, so that the "most correct" system
   values are provided to the renderer.

.. warning::

   The ``renderer`` argument to the ``@view_config`` configuration decorator
   shown above is the template *path*.  In the example above, the path
   ``templates/foo.pt`` is *relative*.  Relative to what, you ask?  Because
   we're using a Chameleon renderer, it means "relative to the directory in
   which the file that defines the view configuration lives".  In this case,
   this is the directory containing the file that defines the ``my_view``
   function.

Similar renderer configuration can be done imperatively.  See
:ref:`views_which_use_a_renderer`.

.. seealso::

    See also :ref:`built_in_renderers`.

Although a renderer path is usually just a simple relative pathname, a path
named as a renderer can be absolute, starting with a slash on UNIX or a drive
letter prefix on Windows.  The path can alternatively be an :term:`asset
specification` in the form ``some.dotted.package_name:relative/path``, making
it possible to address template assets which live in another package.

Not just any template from any arbitrary templating system may be used as a
renderer.  Bindings must exist specifically for :app:`Pyramid` to use a
templating language template as a renderer.

.. sidebar:: Why Use a Renderer via View Configuration

   Using a renderer in view configuration is usually a better way to render
   templates than using any rendering API directly from within a :term:`view
   callable` because it makes the view callable more unit-testable.  Views
   which use templating or rendering APIs directly must return a
   :term:`Response` object.  Making testing assertions about response objects
   is typically an indirect process, because it means that your test code often
   needs to somehow parse information out of the response body (often HTML).
   View callables configured with renderers externally via view configuration
   typically return a dictionary, as above.  Making assertions about results
   returned in a dictionary is almost always more direct and straightforward
   than needing to parse HTML.

By default, views rendered via a template renderer return a :term:`Response`
object which has a *status code* of ``200 OK``, and a *content-type* of
``text/html``.  To vary attributes of the response of a view that uses a
renderer, such as the content-type, headers, or status attributes, you must use
the API of the :class:`pyramid.response.Response` object exposed as
``request.response`` within the view before returning the dictionary.  See
:ref:`request_response_attr` for more information.

The same set of system values are provided to templates rendered via a renderer
view configuration as those provided to templates rendered imperatively.  See
:ref:`renderer_system_values`.

.. index::
   pair: debugging; templates

.. _debugging_templates:

Debugging Templates
-------------------

A :exc:`NameError` exception resulting from rendering a template with an
undefined variable (e.g. ``${wrong}``) might end up looking like this:

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

The output tells you which template the error occurred in, as well as
displaying the arguments passed to the template itself.

.. index::
   single: automatic reloading of templates
   single: template automatic reload

.. _reload_templates_section:

Automatically Reloading Templates
---------------------------------

It's often convenient to see changes you make to a template file appear
immediately without needing to restart the application process. :app:`Pyramid`
allows you to configure your application development environment so that a
change to a template will be automatically detected, and the template will be
reloaded on the next rendering.

.. warning::

   Auto-template-reload behavior is not recommended for production sites as it
   slows rendering slightly; it's usually only desirable during development.

In order to turn on automatic reloading of templates, you can use an
environment variable or a configuration file setting.

To use an environment variable, start your application under a shell using the
``PYRAMID_RELOAD_TEMPLATES`` operating system environment variable set to
``1``, For example:

.. code-block:: text

   $ PYRAMID_RELOAD_TEMPLATES=1 $VENV/bin/pserve myproject.ini

To use a setting in the application ``.ini`` file for the same purpose, set the
``pyramid.reload_templates`` key to ``true`` within the application's
configuration section, e.g.:

.. code-block:: ini
   :linenos:

   [app:main]
   use = egg:MyProject
   pyramid.reload_templates = true

.. index::
   single: template system bindings
   single: Chameleon
   single: Jinja2
   single: Mako

.. _available_template_system_bindings:

Available Add-On Template System Bindings
-----------------------------------------

The Pylons Project maintains several packages providing bindings to different
templating languages including the following:

+---------------------------+----------------------------+--------------------+
| Template Language         | Pyramid Bindings           | Default Extensions |
+===========================+============================+====================+
| Chameleon_                | pyramid_chameleon_         | .pt, .txt          |
+---------------------------+----------------------------+--------------------+
| Jinja2_                   | pyramid_jinja2_            | .jinja2            |
+---------------------------+----------------------------+--------------------+
| Mako_                     | pyramid_mako_              | .mak, .mako        |
+---------------------------+----------------------------+--------------------+

.. _Chameleon: http://chameleon.readthedocs.org/en/latest/
.. _pyramid_chameleon:
   http://docs.pylonsproject.org/projects/pyramid-chameleon/en/latest/

.. _Jinja2: http://jinja.pocoo.org/docs/dev/
.. _pyramid_jinja2:
   http://docs.pylonsproject.org/projects/pyramid-jinja2/en/latest/

.. _Mako: http://www.makotemplates.org/
.. _pyramid_mako:
   http://docs.pylonsproject.org/projects/pyramid-mako/en/latest/
