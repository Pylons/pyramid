from repoze.bfg.template import render_template_to_response
from repoze.bfg.template import render_transform_to_response

def zpt_default_view(context, request):
    return render_template_to_response("default.pt", 
                                       name=context.__name__, 
                                       node=context)

def xslt_view(context, request):
    return render_transform_to_response("xsltview.xsl", context)
