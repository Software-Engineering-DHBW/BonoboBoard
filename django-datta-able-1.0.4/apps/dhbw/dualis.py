# -*- coding: utf-8 -*-

"""
"""

import re
from bs4 import BeautifulSoup

from util import (
    ImporterSession, reqget, reqpost,
    url_get_args, url_get_fqdn
)


def trim_str(content, empty_string=""):
    """

    Parameters
    ----------
    content: str
        string with leading/trailing whitespaces/tabs
    empty_string: str
        string value in case that the value of content is None

    Returns
    -------
    content: str
        string with removed leading/trailing whitespaces/tabs
    """
    if not content:
        content = empty_string
    else:
        content = re.sub(r"^[\t\s]*|[\t\s]*$", "", content)
    return content


def repl_comma_with_dot(content):
    """replaces every comma with a dot"""
    return re.sub(r",", ".", content)


def fit_credits(credits_string):
    """fits the string containing the credits to int"""
    _credits = 0
    if credits_string:
        credits_string = repl_comma_with_dot(trim_str(credits_string))
        _credits = int(float(credits_string))
    return _credits


def fit_grade(grade_string):
    """fits the string containing the grade to float"""
    grade = 0.0
    if grade_string:
        grade_string = repl_comma_with_dot(trim_str(grade_string))
        if re.match(r"[0-9]+[,\.][0-9]+", grade_string):
            grade = float(grade_string)
    return grade


def fit_state(state_string):
    """a mapping for state values to shortcut literals"""
    if state_string == "bestanden" or state_string == "Bestanden":
        state_string = "p"
    elif state_string == "Offen" or state_string == "offen":
        state_string = "o"
    else:
        state_string = "f"
    return state_string


def add_module_to_dualis_dict(m_id, m_name, m_href, m_credits, m_grade, m_state):
    """create with the provided values the DualisModuleDict"""
    dualis_module = {
        "id": m_id,
        "name": m_name,
        "href": m_href,
        "credits": fit_credits(m_credits),
        "grade": fit_grade(m_grade),
        "state": fit_state(m_state)
    }
    return dualis_module


class DualisImporter(ImporterSession):
    """class to import data from dualis

    Attributes
    ----------
    url: str
        the given url for dualis
    params: dict
        dict containing the params for the requests

    Methods
    -------
    login(self, username, password): None
        creates a session for the user
    scrape(self): None
        scrape for the website data
    logout(self): None
        removes the session
    """

    url = "https://dualis.dhbw.de/scripts/mgrqispi.dll"

    __slots__ = ("params",)

    def __init__(self):
        super().__init__()
        self.headers["Host"] = url_get_fqdn(DualisImporter.url)
        self.params = {}

    def login(self, username, password):
        """aquire the authentication token

        Parameters
        ----------
        username: str
            username used to login
        password: str
            password used to login

        Returns
        -------
        None
        """

        url = DualisImporter.url

        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = {
            "APPNAME": "CampusNet",
            "PRGNAME": "LOGINCHECK",
            "ARGUMENTS": "clino,usrname,pass,menuno,menu_type,browser,platform",
            "clino": "000000000000001",
            "menuno": "000324",
            "menu_type": "classic",
            "browser": "",
            "platform": "",
            "usrname": username,
            "pass": password
        }

        r_login = reqpost(
            url=url,
            headers=self.headers,
            payload=data
        )

        self.drop_header("Content-Type")

        for keyval in url_get_args(r_login.headers["REFRESH"]):
            temp = keyval.split("=")
            self.params[temp[0]] = temp[1]

        self.params["PRGNAME"] = "MLSSTART"
        self.params["ARGUMENTS"] = self.params["ARGUMENTS"].split(",")[:2]

        self.auth_token = re.sub(r"[\s]|(;.*)", "", r_login.headers["Set-Cookie"])
        self.headers["Cookie"] = self.auth_token

    def _fill_grades_into_dict(self, response_text):
        """extract needed data and fills the dictionary

        Parameters
        ----------
        response_text: str
            the response text of the request
        Returns
        -------
        None
        """

        grades_content = BeautifulSoup(response_text, "lxml")
        grades_tables = grades_content.find_all("table")

        # fill gpa fields
        i = 0
        temp = grades_tables[1].find_all("th")
        while i < len(temp):
            if temp[i].string == "Gesamt-GPA":
                self.scraped_data["gpa_total"] = fit_grade(temp[i + 1].string)
                i += 2
            else:
                self.scraped_data["gpa_main_subject"] = fit_grade(temp[i + 1].string)
                break

        # fill modules field
        self.scraped_data["modules"] = []
        i = 0
        temp = grades_tables[0].find_all("td")
        while i < len(temp):
            if not temp[i].get("class"):
                i += 1
                continue

            elif "tbdata" in temp[i].get("class"):
                href = ""
                state = temp[i + 5].img.get("title")
                if not state == "Offen":
                    href = temp[i + 1].a.get("href")
                    name = temp[i + 1].a.string
                else:
                    name = trim_str(temp[i + 1].string)

                self.scraped_data["modules"].append(
                    add_module_to_dualis_dict(
                        m_id=temp[i].string,
                        m_name=name,
                        m_href=href,
                        m_credits=temp[i + 3].string,
                        m_grade=temp[i + 4].string,
                        m_state=state
                    )
                )
                i += 6

            else:
                i += 1

    def scrape(self):
        """scrape the wanted data from the website

        Returns
        -------
        None
        """

        url = DualisImporter.url
        r_home = reqget(
            url=url,
            headers=self.headers,
            params=self.params,
        )

        home_content = BeautifulSoup(r_home.text, "lxml")
        url_grade_overview = home_content.find(id="link000310").a.get("href")
        for keyval in url_get_args(url_grade_overview):
            temp = keyval.split("=")
            self.params[temp[0]] = temp[1]

        self.params["PRGNAME"] = "STUDENT_RESULT"

        r_grades = reqget(
            url=url,
            headers=self.headers,
            params=self.params
        )

        self._fill_grades_into_dict(r_grades.text)

    def logout(self):
        """sends a logout request

        Returns
        -------
        None
        """
        url = DualisImporter.url

        self.params["PRGNAME"] = "LOGOUT"

        reqget(
            url=url,
            headers=self.headers,
            params=self.params
        )

        self.auth_token = ""
