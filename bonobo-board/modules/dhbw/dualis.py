# -*- coding: utf-8 -*-

"""Provide functionality to scrape student grades from dualis.
"""

import re
from bs4 import BeautifulSoup

from .util import ImporterSession, reqget, reqpost, url_get_args, url_get_fqdn
from .util import (
    CredentialsException, LoginRequiredException, ServiceUnavailableException
)

#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

def trim_str(content, empty_string=""):
    """ Trim given string with leading/training whitespaces/tabs.

    Parameters
    ----------
    content : str
        String with leading/trailing whitespaces/tabs.
    empty_string : str
        String value in case that the value of content is None.

    Returns
    -------
    content: str
        String with removed leading/trailing whitespaces/tabs.
    """
    if not content:
        content = empty_string
    else:
        content = re.sub(r"^[\t\s]*|[\t\s]*$", "", content)
    return content


def repl_comma_with_dot(content):
    """Replaces every comma with a dot.

    Parameters
    ----------
    content: str
        String where commas should be replaced by dots.
    """
    return re.sub(r",", ".", content)


def fit_credits(credits_string):
    """Fits the string containing the credits to an integer.

    Parameters
    ----------
    credits_string: str

    """
    _credits = 0
    if credits_string:
        credits_string = repl_comma_with_dot(trim_str(credits_string))
        _credits = int(float(credits_string))
    return _credits


def fit_grade(grade_string):
    """Fits the string containing the grade to a float.

    Parameters
    ----------
    grade_string: str

    """
    grade = 0.0
    if grade_string:
        grade_string = repl_comma_with_dot(trim_str(grade_string))
        if re.match(r"[0-9]+[,\.][0-9]+", grade_string):
            grade = float(grade_string)
    return grade


def fit_state(state_string):
    """Provides mapping for state values to shortcut literals.

    Parameters
    ----------
    state_string: str

    """
    if state_string in ("bestanden", "Bestanden"):
        state_string = "p"
    elif state_string in ("offen", "Offen"):
        state_string = "o"
    else:
        state_string = "f"
    return state_string


def add_module_to_dualis_dict(
        *, m_id, m_name, m_href, m_credits, m_grade, m_state):
    """Create the DualisModuleDict with provided values.

    Parameters
    ----------
    m_id: str

    m_name: str

    m_href: str

    m_credits: str

    m_grade: str

    m_state: str

    """
    dualis_module = {
        "id": m_id,
        "name": m_name,
        "href": m_href,
        "credits": fit_credits(m_credits),
        "grade": fit_grade(m_grade),
        "state": fit_state(m_state)
    }
    return dualis_module

#------------------------------------------------------------------------------#
# D U A L I S - I M P O R T E R
#------------------------------------------------------------------------------#

class DualisImporter(ImporterSession):
    """Class to import data from dualis.

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

    async def login(self, username, password):
        """ Async function to acquire the dualis authentication token.

        Parameters
        ----------
        username: str
            username used to login
        password: str
            password used to login

        Returns
        -------
        DualisImporter
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

        try:
            r_login = reqpost(
                url=url,
                headers=self.headers,
                payload=data
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        finally:
            self.drop_header("Content-Type")

        try:
            for keyval in url_get_args(r_login.headers["REFRESH"]):
                temp = keyval.split("=")
                self.params[temp[0]] = temp[1]
        except KeyError as key_err:
            raise CredentialsException() from key_err

        self.params["PRGNAME"] = "MLSSTART"
        self.params["ARGUMENTS"] = self.params["ARGUMENTS"].split(",")[:2]

        self.auth_token = re.sub(r"[\s]|(;.*)", "", r_login.headers["Set-Cookie"])
        self.headers["Cookie"] = self.auth_token

        self.email = username

        return self

    def _fill_grades_into_dict(self, response_text):
        """Extracts needed data and fills the dictionary.

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
            if temp[i].string == 'Gesamt-GPA':
                self.scraped_data['gpa_total'] = fit_grade(temp[i + 1].string)
                i += 2
            else:
                self.scraped_data['gpa_main_subject'] = fit_grade(temp[i + 1].string)
                break

        # fill modules field
        self.scraped_data['modules'] = []
        i = 0
        temp = grades_tables[0].find_all("td")
        while i < len(temp):
            if not temp[i].get("class"):
                i += 1
                continue

            if "tbdata" in temp[i].get("class"):
                href = ""
                state = temp[i + 5].img.get("title")
                if not state == "Offen" or (state == "Offen" and temp[i + 4].string):
                    href = temp[i + 1].a.get("href")
                    name = temp[i + 1].a.string
                else:
                    name = trim_str(temp[i + 1].string)

                self.scraped_data['modules'].append(
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

    async def scrape(self):
        """Scrape the wanted data from the dualis-website.


        Returns
        -------
        None
        """

        url = DualisImporter.url

        try:
            r_home = reqget(
                url=url,
                headers=self.headers,
                params=self.params,
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        except LoginRequiredException as log_req_err:
            raise log_req_err

        home_content = BeautifulSoup(r_home.text, "lxml")

        # access only possible if authenticated!
        try:
            url_grade_overview = home_content.find(id="link000310").a.get("href")
        except AttributeError as attr_err:
            raise LoginRequiredException from attr_err

        for keyval in url_get_args(url_grade_overview):
            temp = keyval.split("=")
            self.params[temp[0]] = temp[1]

        self.params["PRGNAME"] = "STUDENT_RESULT"

        try:
            r_grades = reqget(
                url=url,
                headers=self.headers,
                params=self.params
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        except LoginRequiredException as log_req_err:
            raise log_req_err

        self._fill_grades_into_dict(r_grades.text)

    def logout(self):
        """Sends a logout request (log the user out of the dualis session).

        Returns
        -------
        None
        """
        url = DualisImporter.url

        self.params["PRGNAME"] = "LOGOUT"

        try:
            reqget(
                url=url,
                headers=self.headers,
                params=self.params
            )
        except ServiceUnavailableException as service_err:
            raise service_err

        self.auth_token = ""
