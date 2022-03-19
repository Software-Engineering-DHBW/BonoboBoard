# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import asyncio
from os import sysconf_names
from unittest import result
from asgiref.sync import async_to_sync, sync_to_async

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, get_user_model, authenticate

from .forms import LoginForm
from .models import BonoboUser

from dhbw.dualis import DualisImporter
from dhbw.lecture_importer import CourseImporter, LectureImporter
from dhbw.moodle import MoodleImporter
from dhbw.zimbra import ZimbraHandler

BonoboUser = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/logout/")

    form = LoginForm(request.POST or None)
    course_list = CourseImporter().course_list
    msg = None
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            course = form.cleaned_data.get("course")
            
            if not is_valid_course(course_list, course):
                msg = 'Unbekannter Kurs'
                return render(request, "accounts/login.html", {"form": form, "msg": msg, "course_list": course_list})
            
            user = authenticate_user(request, username, password, course)
         
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Deine angegebenen DHBW Daten können nicht zum Login verwedent werden.'
        else:
            msg = 'Ungültige Eingabedaten'
 
    return render(request, "accounts/login.html", {"form": form, "msg": msg, "course_list": course_list})


def authenticate_user(request, username, password, course):

    loop = get_new_event_loop()
    dualis_result, moodle_result, zimbra_result, lecture_result = loop.run_until_complete(
        verify_login_credentials(username, password))
    loop.close()
    if dualis_result.auth_token is "":
        return None

    if BonoboUser.objects.filter(email=username).exists():
        bonobo_user = authenticate(request, email=username, password=username)
        if bonobo_user is None:
            return None
    else:
        bonobo_user = BonoboUser.objects.create_user(
            email=username, password=username)

    bonobo_user.user_objects["dualis"] = dualis_result
    bonobo_user.user_objects["moodle"] = moodle_result
    bonobo_user.user_objects["zimbra"] = zimbra_result
    bonobo_user.user_objects["lecture"] = lecture_result

    asyncio.run(load_user_data(bonobo_user, course))

    return bonobo_user


def is_valid_course(course_list, course):
    return (course in course_list)


def get_new_event_loop():
    asyncio.set_event_loop(asyncio.new_event_loop())
    return asyncio.get_event_loop()


async def verify_login_credentials(username, password):
    dualis_result = asyncio.ensure_future(
        DualisImporter().login(username, password))
    moodle_result = asyncio.ensure_future(
        MoodleImporter().login(username, password))
    zimbra_result = asyncio.ensure_future(
        ZimbraHandler().login(username, password))
    lecture_result = asyncio.ensure_future(
        LectureImporter().login())
    await asyncio.gather(dualis_result, moodle_result, zimbra_result, lecture_result)
    return dualis_result.result(), moodle_result.result(), zimbra_result.result(), lecture_result.result()


async def load_user_data(bonobo_user, course):
    dualis_future = asyncio.ensure_future(
        bonobo_user.user_objects["dualis"].scrape())
    moodle_future = asyncio.ensure_future(
        bonobo_user.user_objects["moodle"].scrape())
    zimbra_future = asyncio.ensure_future(
        bonobo_user.user_objects["zimbra"].scrape())
    course_uid = CourseImporter().get_course_uid(course)
    lecture_future = asyncio.ensure_future(
        bonobo_user.user_objects["lecture"].scrape(course_uid))

    await asyncio.gather(dualis_future, moodle_future, zimbra_future, lecture_future)


def write_log(msg):
    f = open("log.txt", "a")
    f.write(str(msg)+"\n")
    f.close()
