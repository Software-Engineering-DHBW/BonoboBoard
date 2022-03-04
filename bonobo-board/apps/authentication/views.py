# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model

from .forms import LoginForm
from .models import BonoboUser

from dhbw.dualis import DualisImporter
from dhbw.lecture_importer import CourseImporter, LectureImporter
from dhbw.moodle import MoodleImporter
from dhbw.zimbra import ZimbraHandler

BonoboUser = get_user_model()

def authenticate_user(username, password, course):
    # TODO
    bonobo_user = BonoboUser.objects.create_user(username)
    course_uid = CourseImporter().get_course_uid(course)
    bonobo_user.user_objects["dualis"] = DualisImporter()
    bonobo_user.user_objects["lecture"] = LectureImporter(course_uid)
    bonobo_user.user_objects["moodle"] = MoodleImporter()
    bonobo_user.user_objects["zimbra"] = ZimbraHandler()
    
    for elem in ["dualis", "moodle", "zimbra"]:
        bonobo_user.user_objects[elem].login(username, password)
        if not bonobo_user.user_objects[elem].auth_token:
            return None
        bonobo_user.user_objects[elem].scrape()

    return bonobo_user

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
            user = authenticate_user(username, password, course)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})
