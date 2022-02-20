# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from .forms import LoginForm
from modules.dhbw.dualis import DualisImporter


def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            dualis_entries = getDualisResults(email, password)

            return render(request, 'home/index.html', {"content": dualis_entries})

    else:
        form = LoginForm()

    return render(request, 'home/index.html', {'form': form})


def leistungsuebersicht(request):
    return render(request, 'home/leistungsuebersicht.html')

def email(request):
    return render(request, 'home/email.html')

def vorlesungsplan(request):
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


def getDualisResults(email, password):
    dualis_importer = DualisImporter()
    dualis_importer.login(email, password)
    dualis_importer.scrape()
    dualis_importer.logout()
    return dualis_importer.scraped_data
