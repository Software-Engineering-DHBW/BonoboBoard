# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import asyncio

# Create your views here.
import json

from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model, authenticate
from django.views.decorators.csrf import csrf_protect

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .forms import LoginForm
from .models import BonoboUser

from dhbw.util import CredentialsException, LoginRequiredException, ServiceUnavailableException
from dhbw.dualis import DualisImporter
from dhbw.lecture_importer import CourseImporter, LectureImporter
from dhbw.moodle import MoodleImporter
from dhbw.zimbra import ZimbraHandler

from dhbw.lecture_importer import LectureImporter, read_lectures_from_database, write_lectures_to_database

BonoboUser = get_user_model()


@csrf_protect
def login_view(request):
    """on login view is opened, show window login.html
    authenticate user
    scrape data for user

    Parameters
    ----------
    request: HttpRequest
        request of the page
    Returns
    -------
    HttpResponse
    """
    if request.user.is_authenticated:
        return redirect("/logout/")

    course_importer = CourseImporter()
    course_list = course_importer.course_list
    msg = "Gib deine DHBW Login-Daten ein."
    write_log("before post")
    if request.method == "POST":
        form = LoginForm(request.POST)
        write_log("get form")
        if form.is_valid():
            write_log("form valid")
            username = form.cleaned_data.get("username").strip()
            password = form.cleaned_data.get("password").strip()
            course = form.cleaned_data.get("course").strip()
            if not username or not password or not course:
                write_log("user empty")
                msg = 'Ungültige Eingabedaten'
                return render(request, "accounts/login.html", {"form": form, "msg": msg, "course_list": course_list})

            if not is_valid_course(course_list, course):
                msg = 'Unbekannter Kurs'
                return render(request, "accounts/login.html", {"form": form, "msg": msg, "course_list": course_list})
            lectures_json = lecture_handler(course_importer.get_course_uid(course))
            user, err_msg = authenticate_user(request, username, password, course, lectures_json)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = err_msg
        else:
            msg = 'Ungültige Eingabedaten'
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, "msg": msg, "course_list": course_list})


def lecture_handler(course):
    """ Handles database communication. Pulls latest entries in lectures.db or creates the table if it does not exist.

    Parameters
    ----------
    course : str
        uid of the course to get the lectures from
    Returns
    -------
    json
    """
    try:
        lecture_df = read_lectures_from_database(course)
    except Exception:
        lecture_importer = LectureImporter()
        lecture_importer.scrape(course)
        write_lectures_to_database(lecture_importer.lectures, course)
        lecture_df = read_lectures_from_database(course)
    return lecture_df.to_json()


def encrypt_dict(data_dict, key):
    """ https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password

    Parameters
    ----------
    key : str

    data_dict : dict

    Returns
    -------
    bytes
    """

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(1),
        iterations=50,
    )

    key_gen = base64.urlsafe_b64encode(kdf.derive(key.encode()))
    dump_dict = json.dumps(data_dict)
    fernet = Fernet(key_gen)
    enc_msg = fernet.encrypt(dump_dict.encode())
    return enc_msg


def authenticate_user(request, username, password, course, lectures_json):
    """on login view is opened, show window login.html
    authenticate user
    scrape data for user

    Parameters
    ----------
    lectures_json : json
        return of lecture_handler (gathers lectures from db)
    request: HttpRequest
        request of the page
    username: str
        email of user
    password: str
        password of user
    course: str
        course given by user
    Returns
    -------
    HttpResponse
    """
    loop = get_new_event_loop()
    err_msg, dualis_result, moodle_result, zimbra_result = loop.run_until_complete(
        verify_login_credentials(username, password))
    loop.close()
    # if user can't be logged in into one or more dhbw services, don't allow login into bonoboboard
    if err_msg:
        return None, err_msg

    if BonoboUser.objects.filter(email=username).exists():
        # No password should be stored --> pre-defined password-field is set to the username
        bonobo_user = authenticate(request, email=username, password=username)
        if bonobo_user is None:
            return None, "Benutzer AUA!!!"
    else:
        bonobo_user = BonoboUser.objects.create_user(
            email=username, password=username)

    bonobo_user.user_objects["dualis"] = dualis_result
    bonobo_user.user_objects["moodle"] = moodle_result
    bonobo_user.user_objects["zimbra"] = zimbra_result

    loop = get_new_event_loop()
    status = loop.run_until_complete(load_user_data(bonobo_user, course))
    loop.close()

    if status:
        return None, status

    bonobo_user.user_objects["zimbra"].get_contacts()

    # save scraped data to user in db
    bonobo_user.dualis_scraped_data = encrypt_dict(
        bonobo_user.user_objects["dualis"].scraped_data, bonobo_user.email)  # no plain text in db

    bonobo_user.zimbra_token = bonobo_user.user_objects["zimbra"].auth_token
    bonobo_user.zimbra_accountname = bonobo_user.user_objects["zimbra"].accountname  # Mail sxxxx@student-mannheim.de
    bonobo_user.zimbra_name = bonobo_user.user_objects["zimbra"].realname
    bonobo_user.zimbra_contacts = bonobo_user.user_objects["zimbra"].contacts
    bonobo_user.zimbra_headers = bonobo_user.user_objects["zimbra"].headers

    bonobo_user.moodle_token = bonobo_user.user_objects["moodle"].auth_token
    bonobo_user.moodle_scraped_data = bonobo_user.user_objects["moodle"].scraped_data

    bonobo_user.lectures = lectures_json

    bonobo_user.save()
    return bonobo_user, ""


def is_valid_course(course_list, course):
    """Check if course is in course_list

    Parameters
    ----------
    course_list: List[str]
        list of all courses
    course: str
        given course by user
    Returns
    -------
    Boolean
    """
    return (course in course_list)


def get_new_event_loop():
    """get eventloop of asnycio

    Returns
    -------
    AbstractEventLoop
    """
    asyncio.set_event_loop(asyncio.new_event_loop())
    return asyncio.get_event_loop()


async def verify_login_credentials(username, password):
    """Log into all dhbw services async

    Parameters
    ----------
    username: str
        email of user
    password: str
        password of user
    Returns
    -------
    DualisImporter, MoodleImporter, ZimbraHandler, LectureImporter
    """
    dualis_result = asyncio.ensure_future(
        DualisImporter().login(username, password))
    moodle_result = asyncio.ensure_future(
        MoodleImporter().login(username, password))
    zimbra_result = asyncio.ensure_future(
        ZimbraHandler().login(username, password))

    error_msg = ""

    try:
        await asyncio.gather(dualis_result, moodle_result, zimbra_result)
    except ServiceUnavailableException as service_err:
        error_msg = f"{service_err}"
        return error_msg, None, None, None
    except CredentialsException as cred_err:
        error_msg = f"{cred_err}"
        return error_msg, None, None, None
    return error_msg, dualis_result.result(), moodle_result.result(), zimbra_result.result()


async def load_user_data(bonobo_user, course):
    """Scrape all userdata from all dhbw services async

    Parameters
    ----------
    bonobo_user: BonoboUser
        user object
    course: str
        course given by user
    Returns
    -------
    DualisImporter, MoodleImporter, ZimbraHandler, LectureImporter
    """
    dualis_future = asyncio.ensure_future(
        bonobo_user.user_objects["dualis"].scrape())
    moodle_future = asyncio.ensure_future(
        bonobo_user.user_objects["moodle"].scrape())
    zimbra_future = asyncio.ensure_future(
        bonobo_user.user_objects["zimbra"].scrape())

    try:
        await asyncio.gather(dualis_future, moodle_future, zimbra_future)
    except LoginRequiredException as login_err:
        error_msg = f"{login_err}"
        return error_msg
    except ServiceUnavailableException as service_err:
        error_msg = f"{service_err}"
        return error_msg
    return None


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
    f.write(str(msg) + "\n")
    f.close()
