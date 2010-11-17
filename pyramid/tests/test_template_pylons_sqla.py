# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPylonsSQLA(TestBase):
    """Pylons SQLAlchemy project"""
    template = 'pylons_sqla' 
    def test_project_paster_create(self):
        self.paster_create()
    

