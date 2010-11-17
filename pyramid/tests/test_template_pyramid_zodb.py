# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPyramidZODB(TestBase):
    """pyramid ZODB starter project"""
    template = 'pyramid_zodb' 
    def test_project_paster_create(self):
        self.paster_create()
    

