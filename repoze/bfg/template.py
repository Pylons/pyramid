# The definitions in this module are import aliases for backwards
# compatibility; there are no plans to make this module itself go
# away, but the ``get_template``, ``render_template``, and
# ``render_template_to_response`` APIs should be imported from
# ``repoze.bfg.chameleon_zpt`` in the future for optimum correctness,
# while the ``render_transform`` and ``render_transform_to_response``
# APIs should be imported from ``repoze.bfg.xsl``.

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.xslt import render_transform
from repoze.bfg.xslt import render_transform_to_response
