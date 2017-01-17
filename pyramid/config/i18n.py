from pyramid.interfaces import (
    ILocaleNegotiator,
    ITranslationDirectories,
    )

from pyramid.exceptions import ConfigurationError
from pyramid.path import AssetResolver
from pyramid.util import action_method

class I18NConfiguratorMixin(object):
    @action_method
    def set_locale_negotiator(self, negotiator):
        """
        Set the :term:`locale negotiator` for this application.  The
        :term:`locale negotiator` is a callable which accepts a
        :term:`request` object and which returns a :term:`locale
        name`.  The ``negotiator`` argument should be the locale
        negotiator implementation or a :term:`dotted Python name`
        which refers to such an implementation.

        Later calls to this method override earlier calls; there can
        be only one locale negotiator active at a time within an
        application.  See :ref:`activating_translation` for more
        information.

        .. note::

           Using the ``locale_negotiator`` argument to the
           :class:`pyramid.config.Configurator` constructor can be used to
           achieve the same purpose.
        """
        def register():
            self._set_locale_negotiator(negotiator)
        intr = self.introspectable('locale negotiator', None,
                                   self.object_description(negotiator),
                                   'locale negotiator')
        intr['negotiator'] = negotiator
        self.action(ILocaleNegotiator, register, introspectables=(intr,))

    def _set_locale_negotiator(self, negotiator):
        locale_negotiator = self.maybe_dotted(negotiator)
        self.registry.registerUtility(locale_negotiator, ILocaleNegotiator)

    @action_method
    def add_translation_dirs(self, *specs, **kw):
        """ Add one or more :term:`translation directory` paths to the
        current configuration state.  The ``specs`` argument is a
        sequence that may contain absolute directory paths
        (e.g. ``/usr/share/locale``) or :term:`asset specification`
        names naming a directory path (e.g. ``some.package:locale``)
        or a combination of the two.

        Example:

        .. code-block:: python

           config.add_translation_dirs('/usr/share/locale',
                                       'some.package:locale')

        The translation directories are defined as a list in which
        translations defined later have precedence over translations defined
        earlier.

        By default, consecutive calls to ``add_translation_dirs`` will add
        directories to the start of the list. This means later calls to
        ``add_translation_dirs`` will have their translations trumped by
        earlier calls. If you explicitly need this call to trump an earlier
        call then you may set ``override`` to ``True``.

        If multiple specs are provided in a single call to
        ``add_translation_dirs``, the directories will be inserted in the
        order they're provided (earlier items are trumped by later items).

        .. versionchanged:: 1.8

           The ``override`` parameter was added to allow a later call
           to ``add_translation_dirs`` to override an earlier call, inserting
           folders at the beginning of the translation directory list.

        """
        introspectables = []
        override = kw.pop('override', False)
        if kw:
            raise TypeError('invalid keyword arguments: %s', sorted(kw.keys()))

        def register():
            directories = []
            resolver = AssetResolver(self.package_name)

            # defer spec resolution until register to allow for asset
            # overrides to take place in an earlier config phase
            for spec in specs:
                # the trailing slash helps match asset overrides for folders
                if not spec.endswith('/'):
                    spec += '/'
                asset = resolver.resolve(spec)
                directory = asset.abspath()
                if not asset.isdir():
                    raise ConfigurationError('"%s" is not a directory' %
                                            directory)
                intr = self.introspectable('translation directories', directory,
                                        spec, 'translation directory')
                intr['directory'] = directory
                intr['spec'] = spec
                introspectables.append(intr)
                directories.append(directory)

            tdirs = self.registry.queryUtility(ITranslationDirectories)
            if tdirs is None:
                tdirs = []
                self.registry.registerUtility(tdirs, ITranslationDirectories)
            if override:
                tdirs.extend(directories)
            else:
                for directory in reversed(directories):
                    tdirs.insert(0, directory)

        self.action(None, register, introspectables=introspectables)

