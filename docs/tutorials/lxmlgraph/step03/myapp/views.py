from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.xslt import render_transform_to_response

def zpt_view(context, request):
    return render_template_to_response("templates/default.pt", 
                                       name=context.__name__, 
                                       node=context)

def xslt_view(context, request):
    return render_transform_to_response('templates/xsltview.xsl', context)
