# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from http.client import HTTPResponse
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from .forms import LoginForm
from modules.dhbw.dualis import DualisImporter

is_user_logged_in = False
dualis_entries = []

def index(request):
    if request.method == 'POST':
        return HTTPResponse("brah")
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            
            fetch_user_data(email, password)

            is_user_logged_in = True
            return render(request, 'home/index.html', {'is_user_logged_in': is_user_logged_in})
           
    else:
        form = LoginForm()

    return render(request, 'home/index.html', {'form': form})


def leistungsuebersicht(request):
    if not is_user_logged_in:
        return HttpResponseRedirect('/')
    
    return render(request, 'home/leistungsuebersicht.html',{"content": dualis_entries})


def email(request):
    if not is_user_logged_in:
        return HttpResponseRedirect('/')
    return render(request, 'home/email.html')


def vorlesungsplan(request):
    if not is_user_logged_in:
        return HttpResponseRedirect('/')
    return render(request, 'home/vorlesungsplan.html')


def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def fetch_user_data(email, password):
    global dualis_entries 
    dualis_entries = get_dualis_results(email, password)

def get_dualis_results(email, password):
    dualis_importer = DualisImporter()
    dualis_importer.login(email, password)
    dualis_importer.scrape()
    dualis_importer.logout()
    return dualis_importer.scraped_data


