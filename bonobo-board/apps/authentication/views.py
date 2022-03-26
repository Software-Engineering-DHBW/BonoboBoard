# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import asyncio

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model, authenticate

from .forms import LoginForm
from .models import BonoboUser

from dhbw.util import CredentialsException, LoginRequiredException, ServiceUnavailableException
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

            user, err_msg = authenticate_user(request, username, password, course)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = err_msg
        else:
            msg = 'Ungültige Eingabedaten'

    return render(request, "accounts/login.html", {"form": form, "msg": msg, "course_list": course_list})


def authenticate_user(request, username, password, course):
    loop = get_new_event_loop()
    err_msg, dualis_result, moodle_result, zimbra_result, lecture_result = loop.run_until_complete(
        verify_login_credentials(username, password))
    loop.close()
    if err_msg:
        return None, err_msg

    if BonoboUser.objects.filter(email=username).exists():
        bonobo_user = authenticate(request, email=username, password=username)
        if bonobo_user is None:
            return None, "Benutzer AUA!!!"
    else:
        bonobo_user = BonoboUser.objects.create_user(
            email=username, password=username)

    bonobo_user.user_objects["dualis"] = dualis_result
    bonobo_user.user_objects["moodle"] = moodle_result
    bonobo_user.user_objects["zimbra"] = zimbra_result
    bonobo_user.user_objects["lecture"] = lecture_result

    asyncio.run(load_user_data(bonobo_user, course))

    # request.session["dualis_scraped_data"] = bonobo_user.user_objects["dualis"].scraped_data
    bonobo_user.dualis_scraped_data = bonobo_user.user_objects["dualis"].scraped_data

    bonobo_user.zimbra_token = bonobo_user.user_objects["zimbra"].auth_token
    bonobo_user.zimbra_accountname = bonobo_user.user_objects["zimbra"].accountname  # Mail sxxxx@student-mannheim.de
    bonobo_user.zimbra_name = bonobo_user.user_objects["zimbra"].realname
    bonobo_user.zimbra_contacts = bonobo_user.user_objects["zimbra"].contacts
    bonobo_user.zimbra_headers = bonobo_user.user_objects["zimbra"].headers

    bonobo_user.moodle_token = bonobo_user.user_objects["moodle"].auth_token
    # request.session["moodle_scraped_data"] = bonobo_user.user_objects["moodle"].scraped_data
    bonobo_user.moodle_scraped_data = bonobo_user.user_objects["moodle"].scraped_data

    bonobo_user.lectures = bonobo_user.user_objects["lecture"].lectures.to_json()
    bonobo_user.save()
    return bonobo_user, ""


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

    error_msg = ""

    try:
        await asyncio.gather(dualis_result, moodle_result, zimbra_result, lecture_result)
    except ServiceUnavailableException as service_err:
        error_msg = f"{service_err}"
        return error_msg, None, None, None, None
    except CredentialsException as cred_err:
        error_msg = f"{cred_err}"
        return error_msg, None, None, None, None
    return error_msg, dualis_result.result(), moodle_result.result(), zimbra_result.result(), lecture_result.result()


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

    try:
        await asyncio.gather(dualis_future, moodle_future, zimbra_future, lecture_future)
    except LoginRequiredException:
        # TODO something meaningful x)
        pass
    except ServiceUnavailableException:
        # TODO RENDER 500 ERROR
        pass


def write_log(msg):
    f = open("log.txt", "a")
    f.write(str(msg) + "\n")
    f.close()
