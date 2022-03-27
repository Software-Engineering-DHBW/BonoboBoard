# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import ast
from distutils.fancy_getopt import wrap_text
from email import header
import json

import pandas as pd
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from apps.authentication.models import BonoboUser

from dhbw.lecture_importer import LectureImporter, read_lecture_links_from_database, add_lecture_links_to_database
from dhbw.zimbra import ZimbraHandler
from .forms import ContactForm, EditLinkForm

BonoboUser = get_user_model()


@csrf_protect
@login_required(login_url="/login/")
def index(request):
    """on index page is opened, get dualis data and lecture data of user and return home/index.html with data

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """

    bonobo_user = BonoboUser.objects.get(email=request.user)
    lectures, lecture_links = get_lecture_results(bonobo_user)
    return render(request, 'home/index.html', {"dualis_data": bonobo_user.dualis_scraped_data, "lecture_links": lecture_links, "lectures": lectures, "link": "alter_bluebutton_link", "event": "Programmieren"})


@login_required(login_url="/login/")
def leistungsuebersicht(request):
    """on leistungsuebersicht page is opened, return home/leistungsuebersicht.html

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """
    return render(request, 'home/leistungsuebersicht.html')


@login_required(login_url="/login/")
def email(request):
    """on email page is opened, return home/email.html
    on send email click, check input and send mail by ZimbraHandler

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """
    current_user = BonoboUser.objects.get(email=request.user)

    zimbra = ZimbraHandler()
    zimbra.auth_token = current_user.zimbra_token
    zimbra.accountname = current_user.zimbra_accountname
    zimbra.realname = current_user.zimbra_name
    zimbra.contacts = current_user.zimbra_contacts
    zimbra.headers = ast.literal_eval(current_user.zimbra_headers)

    msg = ["error", ""]
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            mail_dict = {
                "recipients": form.cleaned_data.get("empfänger"),
                "rec_cc": form.cleaned_data.get("cc"),
                "rec_bcc": form.cleaned_data.get("bcc"),
                "subject": form.cleaned_data.get("betreff"),
                "cttype": "text/plain",
                "content": form.cleaned_data.get("nachricht"),
            }

            zimbra.send_mail(mail_dict)
            msg = ["info", "Email erfolgreich gesendet!"]
            form = ContactForm()  # clear the from
            return render(request, 'home/email.html', {'form': form, 'msg': msg})
        else:
            msg[1] = "Fehlerhafte Eingabe"

    else:
        form = ContactForm()

    # current_user.user_objects["zimbra"].get_contacts()
    # contacts = current_user.user_objects["zimbra"].contacts
    # user_contacts = []
    # for contact in contacts:
        # user_contacts.append(contact["email"])

    # , 'user_contacts': user_contacts
    return render(request, 'home/email.html', {'form': form, 'msg': msg})


@login_required(login_url="/login/")
def vorlesungsplan(request, offset=0, old_offset=0):
    """on vorlesungsplan page is opened, load user data and return vorlesungsplan.html

    Parameters
    ----------
    offset: int
        offsets lecture data by a number of weeks
    old_offset: int
        offset from previous call
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """
    offset = int(old_offset) + int(offset)
    current_user = BonoboUser.objects.get(email=request.user)

    lectures, lecture_links = get_lecture_results(current_user, offset)

    return render(request, 'home/vorlesungsplan.html', {"lectures": lectures, "lecture_links": lecture_links, "offset": offset})


@login_required(login_url="/login/")
def edit_link(request, event, link=""):
    """on event is clicked, open a popup window

    Parameters
    ----------
    request: HttpRequest
        request of the page
    event: str
        name of the event
    link: str
        link to the event
    Returns
    -------
    HttpResponse
    """
    current_user = BonoboUser.objects.get(email=request.user)
    event=event.replace("!&!", "/")
    event=event.replace("_", " ").strip()
    #replace html tokens with custom ones for making them processable
    link=link.replace("!&!", "/")
    link=link.replace("!&&!","?")
    link=link.replace("!&&&!","#")
    link=link.replace("!&&&&!","%")
    link=link.replace("_", " ").strip()
    if request.method == "POST":
        form = EditLinkForm(request.POST)
        if form.is_valid():
            new_link = form.cleaned_data.get("link")
            new_link = new_link.replace("https://","")
            new_link = new_link.replace("http://","")

          
     
            
            add_lecture_links_to_database(current_user, event, new_link)
            return HttpResponse(status=204) #Code == no content
    else:
        form = EditLinkForm()

    return render(request, 'home/edit_link.html', {'form': form, 'link': link, 'event': event, 'moodle_data': current_user.moodle_scraped_data})


def pages(request):
    """on unknown page is opened, return error.html accordingly

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """
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
    """get dualis data of user

    Parameters
    ----------
    current_user: BonoboUser

    Returns
    -------
    Dict
    """
    # if current_user.user_objects["dualis"] == None:
    #     return
    # return current_user.user_objects["dualis"].scraped_data


def get_lecture_results(current_user, offset=0):
    """get lectures of user

    Parameters
    ----------
    offset: int
        offsets returned data by a number of weeks
    current_user: BonoboUser

    Returns
    -------
    JSON, pd.DataFrame
    """
    lecture_importer = LectureImporter()
    lecture_importer.lectures = pd.read_json(current_user.lectures)

    lecture_importer.lectures["start"] = pd.to_datetime(
        lecture_importer.lectures["start"])
    lecture_importer.lectures["end"] = pd.to_datetime(
        lecture_importer.lectures["end"])

    lecture_links_df = read_lecture_links_from_database(current_user)
    lectures_df = lecture_importer.limit_weeks_in_list(int(offset))

    json_records = lectures_df.reset_index().to_json(orient='records')
    json_links = lecture_links_df.reset_index().to_json(orient='records')
    lectures = json.loads(json_records)
    lecture_links = json.loads(json_links)

    return lectures, lecture_links


def write_log(msg):
    """internally used for logging
    print message to log.txt

    Parameters
    ----------
    msg: str
        Message to print
    Returns
    -------
    None
    """
    f = open("log.txt", "a")
    f.write(str(msg)+"\n")
    f.close()
