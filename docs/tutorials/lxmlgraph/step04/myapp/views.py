from repoze.bfg.xslt import render_transform_to_response

# Some constants
XML_NAMESPACE='http://www.w3.org/XML/1998/namespace'
XML_PREFIX= '{%s}' % XML_NAMESPACE

def xslt_view(context, request):
    # Grab the root of the tree, which should be a <site>
    site = context.getroottree().getroot()
    # Jot down which node we're sitting on as the <context>
    contextid = "'%s'" % context.get(XML_PREFIX+'id')
    return render_transform_to_response("xsltview.xsl", site, 
                                        contextid=contextid)
