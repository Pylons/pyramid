from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer

vars = [
    var('version', '0.1'),
    var('description', 'One-line description of the package'),
#    var('long_description', 'Multi-line description (in reST)'),
#    var('keywords', 'Space-separated keywords/tags'),
#    var('author', 'Author name'),
#    var('author_email', 'Author email'),
#    var('url', 'URL of homepage'),
#    var('license_name', 'License name'),
    var('zip_safe', 'True/False: if the package can be distributed as a .zip file',
        default=False),
]

class BFGProjectTemplate(Template):
    _template_dir = 'paster_template'
    summary = 'repoze.bfg starter project'
    vars = vars
    template_renderer = staticmethod(paste_script_template_renderer)
