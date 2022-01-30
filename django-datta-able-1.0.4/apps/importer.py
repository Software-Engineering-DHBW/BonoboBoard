# -*- coding: utf-8 -*-

"""
"""

import re
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from typing import ClassVar, Type, Dict, List


def reqpost(url="", headers={}, params={}, payload={}, allow_redirects=False, return_code=200):
    """wrapper for a post request with return code check

    Parameters
    ----------
    url : str
        the destination url which should receive the post request
    headers : dict
        a dictionary of used headers for the request
    params : dict
        a dictionary of parameters used for the request
    payload : dict
        a dictionary of proccessable content for the destination application
    allow_redirects : bool
        whether redirects should be followed or not
    return_code : int
        expected return code of the request

    Returns
    -------
    r : requests.models.Response
        response of the request

    Raises
    ------
    RequestException
        if the expected return code differs from the actual return code
    """
    r = requests.post(url=url, headers=headers, params=params,
                      data=payload, allow_redirects=allow_redirects)
    # compare return code with expected return code
    if not r.status_code == return_code:
        raise RequestException(
            f"Expected return code [{ return_code }] differs from actual return code [{ r.status_code }]")
        # KILL THREAD
    return r


def reqget(url="", headers={}, params={}, allow_redirects=False, return_code=200):
    """wrapper for a get request with return code check

    Parameters
    ----------
    url : str
        the destination url which should receive the post request
    headers : dict
        a dictionary of used headers for the request
    params : dict
        a dictionary of parameters used for the request
    allow_redirects : bool
        whether redirects should be followed or not
    return_code : int
        expected return code of the request

    Returns
    -------
    r : requests.models.Response
        response of the request

    Raises
    ------
    RequestException
        if the expected return code differs from the actual return code
    """
    r = requests.get(url=url, headers=headers, params=params,
                     allow_redirects=allow_redirects)
    # compare return code with expected return code
    if not r.status_code == return_code:
        raise RequestException(
            f"Expected return code [{ return_code }] differs from actual return code [{ r.status_code }]")
        # KILL THREAD
    return r


def url_get_fqdn(url):
    """return fqdn of an url

    Parameters
    ----------
    url : str
        the url from which the fqdn should be extracted

    Returns
    -------
    _ : str
        the fqdn of the given url
    """
    return re.sub("(^http[s]?://)|(/.*$)", "", url)


def url_get_path(url):
    """return path of an url

    Parameters
    ----------
    url : str
        the url from which the path should be extracted

    Returns
    -------
    _ : str
        the path of the given url
    """
    return re.sub("(^.*/)|(\?.*$)", "", url)


def url_get_args(url):
    """return array of arguments of an url

    Parameters
    ----------
    url : str
        the url from which the arguments should be extracted

    Returns
    -------
    _ : list
        a list with all the arguments (str), the form of an argument looks
        as follows: "arg=value"
    """
    return re.sub("^.*\?", "", url).split("&")


class Importer(object):
    """base class for every importer

    Attributes
    ----------
    __auth_token : str
        the string representing the authentication cookie for the created session
    __headers: dict
        a dictionary with default headers and their respective values
    __scraped_data: dict
        a dictionary representing the scraped data

    Methods
    -------
    drop_header(self, header) :
        method to drop headers
    login(self) :
        method which should be implemented by subclasses
    scrape(self) :
        method which should be implemented by subclasses
    logout(self) :
        method which should be implemented by subclasses
    """

    __slots__ = ["__auth_token", "__headers", "__scraped_data"]

    def __init__(self):
        self.__auth_token = ""
        self.__headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        }
        self.__scraped_data = {}

    @property
    def auth_token(self):
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, token):
        self.__auth_token = token

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, key, value):
        self.__headers[key] = value

    @property
    def scraped_data(self):
        return self.__scraped_data

    @scraped_data.setter
    def scraped_data(self, key, value):
        self.__scraped_data[key] = value

    def drop_header(self, header):
        """method to drop headers

        Parameters
        ----------
        header: str
            the name of the header which should be dropped

        Returns
        -------
        None
        """
        self.__headers.pop(header)

    # --- DISCUSSION START --- #
    # JH:   Is it worth to define methods here, which subclasses have to implement like java interfaces? #Python_is_not_Java
    # --- DISCUSSION END ----- #
    # def login(self):
    #     """method which should be implemented by subclasses"""
    #     raise NotImplementedError("This method needs to be implemented!")

    def scrape(self):
        """method which should be implemented by subclasses"""
        raise NotImplementedError("This method needs to be implemented!")

    # def logout(self):
    #     """method which should be implemented by subclasses"""
    #     raise NotImplementedError("This method needs to be implemented!")


class MoodleImporter(Importer):
    """class to import data from moodle

    Attributes
    ----------

    Methods
    -------

    """
    __url = "https://moodle.dhbw-mannheim.de/"

    __slots__ = ["__logout_url"]

    def __init__(self, username, password) -> None:
        # base class
        super().__init__()
        self.headers["Host"] = url_get_fqdn(MoodleImporter.__url)

        # attributes
        self.__logout_url = ""

        # methods to call
        self.login(username, password)
        self.scrape()

    def login(self, username, password):
        """acquire the authentication token

        Parameters
        ----------
        username : str
            username used to login
        password : str
            password used to login

        Returns
        -------
        None
        """
        # lazy peon
        url = MoodleImporter.__url

        # STEP 1: TOKEN - GET REQUEST
        r_token = reqget(url=url+"login/index.php", headers=self.headers)

        # extract needed information - logintoken
        self.headers["Cookie"] = r_token.headers["Set-Cookie"].split(";")[0]
        self.headers["Referer"] = url + "login/index.php"
        self.headers["Origin"] = url
        token_html = BeautifulSoup(r_token.text, "lxml")
        for elem in token_html.find(id="login").find_all("input"):
            if elem.get("name") == "logintoken":
                logintoken = elem.get("value")
                break

        # set form data
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "anchor": "",
            "logintoken": logintoken,
            "username": username,
            "password": password
        }

        # STEP 2: LOGIN - POST REQUEST
        r_login = reqpost(url=url+"login/index.php",
                          headers=self.headers, payload=payload, return_code=303)

        # add authentication cookie to the headers
        self.auth_token = r_login.headers["Set-Cookie"].split(";")[0]
        self.headers["Cookie"] = self.auth_token

        # drop content-type header
        self.drop_header("Content-Type")
        self.drop_header("Origin")

    def scrape(self):
        """
        """
        # lazy peon
        url = MoodleImporter.__url

        # renew referer header
        self.headers["Referer"] = url

        # STEP 1: PROFILE - GET REQUEST
        r_profile = reqget(url=url+"user/profile.php", headers=self.headers)

        # parse html content of the response
        content_profile = BeautifulSoup(r_profile.text, "lxml")

        # scrape username
        self.scraped_data["username"] = content_profile.find(
            id="usermenu").get("title")

        # scrape logout url
        for tag_a in content_profile.find(id="usermenu-dropdown").find_all("a"):
            if tag_a.get("title") == "Logout":
                self.__logout_url = tag_a.get("href")

        # scrape for every joined course
        course_dict = {}
        for course in content_profile.find(id="adaptable-tab-coursedetails").find_all("a"):
            course_dict[course.string] = {
                "href": url+"course/view.php?id="+re.sub("^.*=", "", course.get("href")),
                "bbb_rooms": {}
            }

        # find every bbb room under the joined courses
        for key, val in course_dict.items():
            # STEP 2: COURSE - GET REQUEST
            r_course = reqget(url=val["href"], headers=self.headers)
            # parse the html content of the request
            content_course = BeautifulSoup(r_course.text, "lxml")
            # find all links
            for tag_a in content_course.find_all("a"):
                # in case the "a"-tag does not have a href
                if tag_a.get("href") == None:
                    continue
                temp_href = tag_a.get("href")
                # check if the href attribute contains the string
                if "bigbluebuttonbn" in temp_href:
                    # find all span tags
                    for tag_span in tag_a.find_all("span"):
                        # check if the class attribute contains the string
                        if "instancename" in tag_span.get("class"):
                            # check if span contains just one element
                            if len(tag_span.contents) == 1:
                                course_dict[key]["bbb_rooms"][tag_span.string] = temp_href
                            else:
                                # iterate over the elements of the span tag
                                for content in tag_span.contents:
                                    # check if element is of the given type
                                    if isinstance(content, NavigableString):
                                        course_dict[key]["bbb_rooms"][content.string] = temp_href
                            break

        self.scraped_data["courses"] = course_dict

    def logout(self):
        """
        """
        # STEP 1: LOGOUT - GET REQUEST
        reqget(url=self.__logout_url, headers=self.headers, return_code=303)


class ZimbraHandler:
    """
    """
    __url: ClassVar[str] = "https://studgate.dhbw-mannheim.de/zimbra/"

    __auth_token: str
    __headers: Dict[str, str]

    __slots__ = ("__auth_token", "__headers")

    def __init__(self, username: str, password: str) -> None:
        self.__headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Host": url_get_fqdn(ZimbraHandler.__url),
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        }

        self.login(username, password)

    @property
    def auth_token(self) -> str:
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, value: str) -> None:
        self.__auth_token = value

    @property
    def headers(self) -> Dict[str, str]:
        return self.__headers

    @headers.setter
    def headers(self, key: str, value: str) -> None:
        self.__headers[key] = value

    def login(self, username: str, password: str) -> None:
        """
        """
        # lazy peon
        url: str = ZimbraHandler.__url

        # set headers for post request
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Cookie"] = "ZM_TEST=true"

        # form data
        payload: dict[str, str] = {
            "client": "preferred",
            "loginOp": "login",
            "username": username,
            "password": password
        }

        # LOGIN - POST REQUEST
        r_login: Type[requests.models.Response] = reqpost(
            url=url, headers=self.headers, payload=payload, allow_redirects=False, return_code=302)

        # add authentication cookie to the headers
        self.auth_token = r_login.headers["Set-Cookie"].split(";")[0]
        self.headers["Cookie"] = "; ".join(
            self.headers["Cookie"], self.auth_token)

    def scrape(self):
        """
        """
        # lazy peon
        url: str = ZimbraHandler.__url

    def write_mail(self):
        """
        """
        # lazy peon
        url: str = ZimbraHandler.__url
