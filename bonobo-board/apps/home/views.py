# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import ast
import json
import pickle

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

from dhbw.lecture_importer import LectureImporter
from dhbw.zimbra import ZimbraHandler
from .forms import ContactForm

BonoboUser = get_user_model()


@csrf_protect
@login_required(login_url="/login/")
def index(request):
    """on index page is opened, get dualis data of user and return home/index.html with data

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """

    bonobo_user = BonoboUser.objects.get(email=request.user)
    return render(request, 'home/index.html', {"dualis_data": bonobo_user.dualis_scraped_data})


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
            form = ContactForm() # clear the from
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
def vorlesungsplan(request):
    """on vorlesungsplan page is opened, load user data and return vorlesungsplan.html

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """
    current_user = BonoboUser.objects.get(email=request.user)
    lectures = get_lecture_results(current_user)

    return render(request, 'home/vorlesungsplan.html', {"lectures": lectures})


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


def get_lecture_results(current_user):
    """get lectures of user

    Parameters
    ----------
    current_user: BonoboUser
        
    Returns
    -------
    pd.DataFrame
    """
    #lecture_importer = LectureImporter.read_lectures_from_database(uid)
    lecture_importer = LectureImporter()
    lecture_importer.lectures = pd.read_json(current_user.lectures)
    lecture_importer.lectures["start"] = pd.to_datetime(lecture_importer.lectures["start"], unit="ms")
    lecture_importer.lectures["end"] = pd.to_datetime(lecture_importer.lectures["end"], unit="ms")
    write_log("Actual lectures")
    write_log(lecture_importer.lectures)
    lectures_df = lecture_importer.limit_weeks_in_list(0, 0)
    write_log("After trimming")
    write_log(lectures_df)
    json_records = lectures_df.reset_index().to_json(orient='records')
    lectures = json.loads(json_records)

    return lectures


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
