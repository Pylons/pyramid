Templates
=========

A *template* is a file on disk which can be used to render data
provided by a *view* in a form that is meaningful for a particular
*context*.

Default Templating With z3c.pt Page Templates
------------------------------------------------

Like Zope, ``repoze.bfg`` uses Zope Page Templates (ZPT) as its default
templating language. However, ``repoze.bfg`` uses a different
implementation of the ZPT specification: the `z3c.pt
<http://pypi.python.org/pypi/z3c.pt>`_ templating engine. This
templating engine complies with the `Zope Page Template
<http://wiki.zope.org/ZPT/FrontPage>`_ template specification. While
``z3c.pt`` doesn't implement the METAL specification (feature or
drawback, depending on your viewpoint,) it is significantly faster. And
faster, of course, is the zen of ``repoze.bfg``.

Given a template named ``foo.html`` in a directory in your application
named "templates", you can render the template in a view via::

  from repoze.bfg.template import render_template
  render_template('templates/foo.html', foo=1, bar=2)

You can also wire up page templates via ZCML:

.. sourcecode:: xml

  <bfg:view
      for=".models.IMapping"
      view=".views.contents_view"
      name="contents.html"
      />

Both approaches load the template and keep it in memory between
requests. This means that modifications to the ZPT require a restart
before you can see the changes.

Templating with XSLT
------------------------

``repoze.bfg`` also supports XSLT as an optional templating language.
Like ZPT, an XSLT template is loaded once and re-used between requests.

Given a template ``foo.xsl`` in the templates directory, you can render
an XSLT as follows::

  from repoze.bfg.template import render_transform
  from lxml import etree
  node = etree.Element("root")  
  render_transform('templates/foo.xsl', node)

As shown, the second argument to ``render_transform`` is the element
(and children) that you want as the top of the data for the XSLT.

You can also pass XSLT parameters in as keyword arguments::

  from repoze.bfg.template import render_transform
  from lxml import etree
  node = etree.Element("root")
  value1 = "'app1'"
  render_transform('templates/foo.xsl', node, param1=value1)

This would then assign 'app1' as the value of an ``<xsl:param
name="param1"/>`` parameter in the XSLT template.
