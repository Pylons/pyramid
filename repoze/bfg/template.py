# The definitions in this module are import aliases for backwards
# compatibility; there are no plans to make this module itself go
# away, but the ``get_template``, ``render_template``, and
# ``render_template_to_response`` APIs should be imported from
# ``repoze.bfg.chameleon_zpt`` in the future for optimum correctness,
# while the ``render_transform`` and ``render_transform_to_response``
# APIs should be imported from ``repoze.bfg.xslt``.
from zope.deprecation import deprecated

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.xslt import render_transform
from repoze.bfg.xslt import render_transform_to_response

for name in ('get_template', 'render_template', 'render_template_to_response'):
    deprecated(name,
               ('repoze.bfg.template.%s should now be imported as '
                'repoze.bfg.chameleon_zpt.%s' % (name, name)))

for name in ('render_transform', 'render_transform_to_response'):
    deprecated(name,
               ('repoze.bfg.template.%s should now be imported as '
                'repoze.bfg.xslt.%s' % (name, name)))
