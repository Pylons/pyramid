.. _paster_module:

:mod:`pyramid.paster`
---------------------------

.. module:: pyramid.paster

.. function:: get_app(config_file, name=None)

    Return the WSGI application named ``name`` in the PasteDeploy
    config file ``config_file``.

    If the ``name`` is None, this will attempt to parse the name from
    the ``config_file`` string expecting the format ``ini_file#name``.
    If no name is found, the name will default to "main".

