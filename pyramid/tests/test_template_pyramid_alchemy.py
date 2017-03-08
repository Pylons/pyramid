# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPyramidAlchemy(TestBase):
    """pyramid SQLAlchemy project using traversal"""
    template = 'pyramid_alchemy' 
    def test_project_paster_create(self):
        self.paster_create()
    

