# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPylonsBasic(TestBase):
    """Pylons basic project"""
    template = 'pylons_basic' 
    def test_project_paster_create(self):
        self.paster_create()
    

