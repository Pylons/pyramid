.. _translationdir_directive:

``translationdir``
------------------

Add a :term:`gettext` :term:`translation directory` to the current
configuration for use in localization of text.

Attributes
~~~~~~~~~~

``dir``
  The path to the translation directory.  This path may either be 1)
  absolute (e.g. ``/foo/bar/baz``) 2) Python-package-relative
  (e.g. ``packagename:foo/bar/baz``) or 3) relative to the package
  directory in which the ZCML file which contains the directive
  (e.g. ``foo/bar/baz``).

Example 1
~~~~~~~~~

.. code-block:: xml
   :linenos:

   <!-- relative to configure.zcml file -->

   <translationdir
     dir="locale"
     />

Example 2
~~~~~~~~~

.. code-block:: xml
   :linenos:

   <!-- relative to another package -->

   <translationdir
     dir="another.package:locale"
     />

Example 3
~~~~~~~~~

.. code-block:: xml
   :linenos:

   <!-- an absolute directory name -->

   <translationdir
     dir="/usr/share/locale"
     />

Alternatives
~~~~~~~~~~~~

Use :meth:`pyramid.config.Configurator.add_translation_dirs`
method instance during initial application setup.

See Also
~~~~~~~~

See also :ref:`activating_translation`.
