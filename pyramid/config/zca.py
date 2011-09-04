from pyramid.threadlocal import get_current_registry
from zope.component import getSiteManager

class ZCAConfiguratorMixin(object):
    def hook_zca(self):
        """ Call :func:`zope.component.getSiteManager.sethook` with the
        argument :data:`pyramid.threadlocal.get_current_registry`, causing
        the :term:`Zope Component Architecture` 'global' APIs such as
        :func:`zope.component.getSiteManager`,
        :func:`zope.component.getAdapter` and others to use the
        :app:`Pyramid` :term:`application registry` rather than the Zope
        'global' registry."""
        getSiteManager.sethook(get_current_registry)

    def unhook_zca(self):
        """ Call :func:`zope.component.getSiteManager.reset` to undo the
        action of :meth:`pyramid.config.Configurator.hook_zca`."""
        getSiteManager.reset()

