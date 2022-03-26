# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('leistungsuebersicht', views.leistungsuebersicht, name='leistungsuebersicht'),
    path('email', views.email, name='email'),
    path('vorlesungsplan', views.vorlesungsplan, name='vorlesungsplan'),
    path('vorlesungsplan/edit_link/<event>', views.edit_link, name='edit_link'),
    path('vorlesungsplan/edit_link/<event>/<link>', views.edit_link, name='edit_link'),
    path('vorlesungsplan/<offset>/<old_offset>', views.vorlesungsplan, name='vorlesungsplan'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
