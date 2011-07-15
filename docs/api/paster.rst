.. _paster_module:

:mod:`pyramid.paster`
---------------------------

.. automodule:: pyramid.paster

    .. function:: get_app(config_uri, name=None)

        Return the WSGI application named ``name`` in the PasteDeploy
        config file specified by ``config_uri``.

        If the ``name`` is None, this will attempt to parse the name from
        the ``config_uri`` string expecting the format ``inifile#name``.
        If no name is found, the name will default to "main".

    .. autofunction:: bootstrap
