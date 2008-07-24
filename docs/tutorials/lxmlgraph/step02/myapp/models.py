import os

from zope.interface import implements
from zope.interface import Attribute
from zope.interface import Interface
from lxml import etree

class IMyModel(Interface):
    __name__ = Attribute('Name of the model instance')

class BfgElement(etree.ElementBase):
    """Handle access control and getitem behavior"""

    implements(IMyModel)

    @property
    def __name__(self):
        return self.xpath("@name")[0]

    def __getitem__(self, child_name):
        xp = "*[@name='%s']" % child_name
        matches = self.xpath(xp)
        if len(matches) == 0:
            raise KeyError('No child found for %s' % child_name)
        elif len(matches) > 1:
            raise KeyError('More than one child for %s' % child_name)
        else:
            return matches[0]

def get_root(environ):
    # Setup the custom parser with our BfgElement behavior
    parser_lookup = etree.ElementDefaultClassLookup(element=BfgElement)
    parser = etree.XMLParser()
    parser.set_element_class_lookup(parser_lookup)

    # Now load the XML file
    here = os.path.join(os.path.dirname(__file__))
    samplemodel = os.path.join(here, 'samplemodel.xml')
    xmlstring = open(samplemodel).read()
    root = etree.XML(xmlstring, parser)

    return root
