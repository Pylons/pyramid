# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPyramidStarterZCML(TestBase):
    """pyramid starter project (ZCML)"""
    template = 'pyramid_starter_zcml' 
    def test_project_paster_create(self):
        self.paster_create()
    

