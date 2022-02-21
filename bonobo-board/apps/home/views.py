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
from django.views.decorators.csrf import csrf_protect
from .forms import LoginForm, ContactForm
from modules.dhbw.dualis import DualisImporter

is_user_logged_in = False
dualis_entries = []


@csrf_protect
def index(request):
    global is_user_logged_in
    global dualis_entries

    if is_user_logged_in: 
        return render(request, 'home/index.html', {'is_user_logged_in': is_user_logged_in, 'content': dualis_entries})

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("passwort")

            fetch_user_data(email, password)

            is_user_logged_in = True
            return render(request, 'home/index.html', {'is_user_logged_in': is_user_logged_in, 'content': dualis_entries})
           
    else:
        form = LoginForm()

    return render(request, 'home/index.html', {'form': form})


def leistungsuebersicht(request):
    if not is_user_logged_in:
        return HttpResponseRedirect('/')

    return render(request, 'home/leistungsuebersicht.html', {"content": dualis_entries})


def email(request):
    if not is_user_logged_in:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            return render(request, 'home/email.html', {'form': form})
    else:
        form = ContactForm()

    return render(request, 'home/email.html', {'form': form})

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
