# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPyramidStarter(TestBase):
    """pyramid starter project"""
    template = 'pyramid_starter' 
    def test_project_paster_create(self):
        self.paster_create()
    

