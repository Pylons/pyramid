## -*- coding: utf-8 -*-
<%!from pyramid.compat import text_%><% a, b = 'foo', text_('föö', 'utf-8') %>
Hello ${text_('föö', 'utf-8')}