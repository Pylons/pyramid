from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer

class BFGProjectTemplate(Template):
    _template_dir = 'paster_template'
    summary = 'repoze.bfg starter project'
    template_renderer = staticmethod(paste_script_template_renderer)
