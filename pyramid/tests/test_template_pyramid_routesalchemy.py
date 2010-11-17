# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPyramidRoutesAlchemy(TestBase):
    """pyramid SQLAlchemy project using Routes (no traversal)"""
    template = 'pyramid_routesalchemy' 
    def test_project_paster_create(self):
        self.paster_create()
    

