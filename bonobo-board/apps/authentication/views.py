# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model, authenticate

from .forms import LoginForm
from .models import BonoboUser

from dhbw.dualis import DualisImporter
from dhbw.lecture_importer import CourseImporter, LectureImporter
from dhbw.moodle import MoodleImporter
from dhbw.zimbra import ZimbraHandler

BonoboUser = get_user_model()

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            course = form.cleaned_data.get("course")
            # TODO load stored user data from db
            # write own function therefore!
            user = authenticate_user(request, username, password, course)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def authenticate_user(request, username, password, course):

    dualis= DualisImporter()
    moodle = MoodleImporter()
    zimbra = ZimbraHandler()

    for element in [dualis, moodle, zimbra]:
        element.login(username, password)
        #if dualis present -> login
        if not element.auth_token:
            return None
        element.scrape()

    if BonoboUser.objects.filter(email=username).exists():
        bonobo_user = authenticate(request, email=username, password=username)
    if bonobo_user is None:
        return None
    else:
        bonobo_user = BonoboUser.objects.create_user(email=username, password=username)
    
    course_uid = CourseImporter().get_course_uid(course)
    lecture = LectureImporter(course_uid)

    bonobo_user.user_objects["dualis"] = dualis
    bonobo_user.user_objects["lecture"] = lecture
    bonobo_user.user_objects["moodle"] = moodle
    bonobo_user.user_objects["zimbra"] = zimbra

    return bonobo_user
