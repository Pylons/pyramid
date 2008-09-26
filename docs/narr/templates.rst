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
complies with the `Zope Page Template
<http://wiki.zope.org/ZPT/FrontPage>`_ template specification and is
significantly faster.

.. note:: :mod:`repoze.bfg` can also allow for the use of Genshi-style
   templates via the ``chameleon.genshi`` package, support for which
   is built-in to :mod:`repoze.bfg`.  The :mod:`repoze.bfg` API
   functions for getting and rendering Chameleon Genshi-style
   templates mirrors the Chameleon ZPT-style API completely; only the
   template files themselves must differ.  See :ref:`template_module`
   for more information about using Genshi-style templates within
   :mod:`repoze.bfg`.

Given that there is a :term:`chameleon.zpt` template named
``foo.html`` in a directory in your application named ``templates``,
you can render the template from a view like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response
   def sample_view(context, request):
       return render_template_to_response('templates/foo.html', foo=1, bar=2)

The first argument to ``render_template_to_response`` shown above (and
its sister function ``render_template``, not shown, which just returns
a string body) is the template *path*.  Above, the path
``templates/foo.html`` is *relative*.  Relative to what, you ask?
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
       result = render_template('templates/foo.html', foo=1, bar=2)
       response = Response(result)
       response.content_type = 'text/plain'
       return response

:mod:`repoze.bfg` loads the template and keeps it in memory between
requests. This means that modifications to the ZPT require a restart
before you can see the changes.

Templating with XSLT
------------------------

:mod:`repoze.bfg` also supports XSLT as an optional templating
language.  Like ZPT, an XSLT template is loaded once and re-used
between requests.

Given a template ``foo.xsl`` in the templates directory, you can render
an XSLT as follows:

.. code-block:: python
   :linenos:

   from repoze.bfg.xslt import render_transform_to_response
   from lxml import etree
   node = etree.Element("root")  
   return render_transform_to_response('templates/foo.xsl', node)

As shown, the second argument to ``render_transform_to_response`` is
the element (and children) that you want as the top of the data for
the XSLT.

You can also pass XSLT parameters in as keyword arguments:

.. code-block:: python
   :linenos:

   from repoze.bfg.xslt import render_transform_to_response
   from lxml import etree
   node = etree.Element("root")
   value1 = "'app1'"
   return render_transform_to_response('templates/foo.xsl', node, param1=value1)

This would then assign 'app1' as the value of an ``<xsl:param
name="param1"/>`` parameter in the XSLT template.

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
   `repoze.bfg.jinja2
   <http://svn.repoze.org/repoze.bfg.jinja2/trunk/>`_ for an example
   of one such package.  This particular one creates
   :mod:`repoze.bfg`-style bindings for the `Jinja2
   <http://jinja.pocoo.org/2/documentation>`_ templating system.


