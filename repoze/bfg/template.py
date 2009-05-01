# The definitions in this module are import aliases for backwards
# compatibility; there are no plans to make this module itself go
# away, but the ``get_template``, ``render_template``, and
# ``render_template_to_response`` APIs should be imported from
# ``repoze.bfg.chameleon_zpt`` in the future for optimum correctness.
# Two other functions named ``render_transform`` and
# ``render_transform_to_response`` APIs used to be here for XSLT
# support; those no longer exist here; you need to install and use the
# ``repoze.bfg.xslt`` package.
from zope.deprecation import deprecated

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response

for name in ('get_template', 'render_template', 'render_template_to_response'):
    deprecated(name,
               ('repoze.bfg.template.%s should now be imported as '
                'repoze.bfg.chameleon_zpt.%s' % (name, name)))

