Templates
=========

A *template* is a file on disk which can be used to render data
provided by a *view*.

Default Templating With z3c.pt Page Templates
------------------------------------------------

Like Zope, :mod:`repoze.bfg` uses Zope Page Templates (ZPT) as its
default templating language. However, :mod:`repoze.bfg` uses a
different implementation of the ZPT specification: the :term:`z3c.pt`
templating engine. This templating engine complies with the `Zope Page
Template <http://wiki.zope.org/ZPT/FrontPage>`_ template
specification. While :term:`z3c.pt` doesn't implement the *METAL*
specification (feature or drawback, depending on your viewpoint), it
is significantly faster.

Given that there is a template named ``foo.html`` in a directory in
your application named ``templates``, you can render the template from
a view like so::

  from repoze.bfg.template import render_template_to_response

  def sample_view(context, request)
      return render_template_to_response('templates/foo.html', foo=1, bar=2)

The first argument to ``render_template_to_response`` shown above (and
its sister function ``render_template``, not shown, which just returns
a string body) is the template *path*.  Above, the path
``templates/foo.html`` is *relative*.  Relative to what, you ask?
Relative to the directory in which the ``views.py`` file which names
it lives, which is usually the :mod:`repoze.bfg` application's
:term:`package` directory.

``render_template_to_response`` always renders a :term:`z3c.pt`
template, and always returns a Response object which has a *status
code* of ``200 OK`` and a *content-type* of ``text-html``.  If you
need more control over the status code and content-type, use the
``render_template`` function instead, which also renders a z3c.pt
template but returns a string instead of a Response.  You can use
the string manually as a response body::

  from repoze.bfg.template import render_template
  from webob import Response

  def sample_view(context, request)
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
an XSLT as follows::

  from repoze.bfg.template import render_transform_to_response
  from lxml import etree
  node = etree.Element("root")  
  return render_transform_to_response('templates/foo.xsl', node)

As shown, the second argument to ``render_transform_to_response`` is
the element (and children) that you want as the top of the data for
the XSLT.

You can also pass XSLT parameters in as keyword arguments::

  from repoze.bfg.template import render_transform_to_response
  from lxml import etree
  node = etree.Element("root")
  value1 = "'app1'"
  return render_transform_to_response('templates/foo.xsl', node, param1=value1)

This would then assign 'app1' as the value of an ``<xsl:param
name="param1"/>`` parameter in the XSLT template.
