# -*- coding: utf-8 -*-

"""BonoboBoard requires a login, to ensure that the login process works
as expected, this module tests the functionality
"""

# standard python library packages
from os import environ
import unittest
from unittest import TestCase
import re

# pypi packages / third-party packages
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

# own "modules"
from frontend_config import *

def full_url(resource_path):
    """join url and resource path together"""
    return "".join([URL, resource_path])

def check_env_vars_set():
    """check that credentials are set, otherwise fail this test"""
    if not environ.get("STUDENTMAIL") or not environ.get("STUDENTPASS") or not environ.get("STUDENTCOURSE"):
        raise Exception(
            f"To run this unittest, you must set the following variables inside your environment:"
            f"STUDENTMAIL, STUDENTPASS, STUDENTCOURSE"
        )

def get_csrf_token():
    """get the csrf token, which is mandatory for the authentication process"""
    try:
        r_token = requests.get(
            url = full_url("/login/"),
            allow_redirects = False
        )
    except RequestException as request_err:
        raise request_err

    csrf_cookie = re.sub(r"[\s]|(;.*)", "", r_token.headers["Set-Cookie"])
    csrf_token = ""
    content = BeautifulSoup(r_token.text, "lxml")
    tag_input_all = content.find_all("input")
    for tag_input in tag_input_all:
        if tag_input.get("name") == "csrfmiddlewaretoken":
            csrf_token = tag_input.get("value")
            break
    return csrf_token, csrf_cookie

class TestLoginPage(TestCase):
    def test_redirect_to_login(self):
        """if the user is not authenticated, every requested path should redirect to /login"""
        r_redirect = requests.models.Response()
        try:
            app_paths = APPLICATION_PATHS.copy()
            app_paths = [full_url(app_path) for app_path in app_paths]
            app_paths.append(URL)
            for app_path in app_paths:
                r_redirect = requests.get(
                    url = app_path,
                    allow_redirects = False,
                )
                self.assertIn("Location", r_redirect.headers)
                self.assertIn("login", r_redirect.headers["Location"])
        except RequestException:
            # fail on purpose
            self.assertTrue(False)

    def test_login_form(self):
        """login form must have three fields: email, password, course and one hidden field for the csrf token"""
        pass

    def test_authentication(self):
        """"""
        check_env_vars_set()
        form_dict = {
            "username": environ.get("STUDENTMAIL"),
            "password": environ.get("STUDENTPASS"),
            "course": environ.get("STUDENTCOURSE")
        }
        headers = {}
        try:
            csrf_token, csrf_cookie = get_csrf_token()
            form_dict["csrfmiddlewaretoken"] = csrf_token
            headers["Cookie"] = csrf_cookie
            r_login = requests.post(
                url = full_url("/login/"),
                headers = headers,
                data = form_dict,
                allow_redirects = False
            )
        except RequestException:
            # fail on purpose
            self.assertTrue(False)

        content = BeautifulSoup(r_login.text, "lxml")
        status_msg = content.find(id="loading")
        self.assertEqual("Wir beziehen deine DHBW Daten...", status_msg.div.string)

if __name__ == "__main__":
    unittest.main()
