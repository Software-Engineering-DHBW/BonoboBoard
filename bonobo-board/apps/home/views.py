# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import json
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from apps.authentication.models import BonoboUser
from .forms import ContactForm

BonoboUser = get_user_model()

@csrf_protect
@login_required(login_url="/login/")
def index(request):
    content_dump = get_dualis_results(BonoboUser.objects.get(email=request.user))
    return render(request, 'home/index.html', {"content_dump": content_dump})

@login_required(login_url="/login/")
def leistungsuebersicht(request):
    return render(request, 'home/leistungsuebersicht.html')

@login_required(login_url="/login/")
def email(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            #current_user = BonoboUser.objects.get(email=request.user)
            #current_user.user_objects["zimbra"].sendmail()
            return render(request, 'home/email.html', {'form': form})
    else:
        form = ContactForm()

    return render(request, 'home/email.html', {'form': form})

@login_required(login_url="/login/")
def vorlesungsplan(request):
    lectures = get_lecture_results(request.user)
    return render(request, 'home/vorlesungsplan.html', {"lectures": lectures})

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


def get_dualis_results(current_user):
    return current_user.user_objects["dualis"].scraped_data

def get_lecture_results(current_user):
    #lecture_importer = LectureImporter.read_lectures_from_database(uid)
    lecture_importer = current_user.user_objects["lecture"]
    lectures_df = lecture_importer.limit_days_in_list(14, 14)

    json_records = lectures_df.reset_index().to_json(orient='records')
    lectures = json.loads(json_records)

    return lectures
