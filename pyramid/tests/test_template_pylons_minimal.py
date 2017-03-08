# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPylonsMinimal(TestBase):
    """Pylons minimal project"""
    template = 'pylons_minimal' 
    def test_project_paster_create(self):
        self.paster_create()
    

