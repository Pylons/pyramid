.. _configure_directive:

``configure``
-------------

Because :term:`ZCML` is XML, and because XML requires a single root
tag for each document, every ZCML file used by :mod:`pyramid` must
contain a ``configure`` container directive, which acts as the root
XML tag.  It is a "container" directive because its only job is to
contain other directives.

Attributes
~~~~~~~~~~

``xmlns``
   The default XML namespace used for subdirectives.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <configure xmlns="http://pylonshq.com/pyramid">

      <!-- other directives -->

   </configure>

.. _word_on_xml_namespaces:

A Word On XML Namespaces
~~~~~~~~~~~~~~~~~~~~~~~~

Usually, the start tag of the ``<configure>`` container tag has a
default *XML namespace* associated with it. This is usually
``http://pylonshq.com/pyramid``, named by the ``xmlns`` attribute of
the ``configure`` start tag.

Using the ``http://pylonshq.com/pyramid`` namespace as the default XML
namespace isn't strictly necessary; you can use a different default
namespace as the default.  However, if you do, the declaration tags
which are defined by :mod:`pyramid` such as the ``view`` declaration
tag will need to be defined in such a way that the XML parser that
:mod:`pyramid` uses knows which namespace the :mod:`pyramid` tags are
associated with.  For example, the following files are all completely
equivalent:

.. topic:: Use of A Non-Default XML Namespace

  .. code-block:: xml
     :linenos:

      <configure xmlns="http://namespaces.zope.org/zope"
                 xmlns:pyramid="http://pylonshq.com/pyramid">

        <include package="pyramid.includes" />

        <pyramid:view
           view="helloworld.hello_world"
           />

      </configure>

.. topic:: Use of A Per-Tag XML Namespace Without A Default XML Namespace

  .. code-block:: xml
     :linenos:

      <configure>

        <include package="pyramid.includes" />

        <view xmlns="http://pylonshq.com/pyramid"
           view="helloworld.hello_world"
           />

      </configure>

For more information about XML namespaces, see `this older, but simple
XML.com article <http://www.xml.com/pub/a/1999/01/namespaces.html>`_.

The conventions in this document assume that the default XML namespace
is ``http://pylonshq.com/pyramid``.

Alternatives
~~~~~~~~~~~~

None.

See Also
~~~~~~~~

See also :ref:`helloworld_declarative`.

