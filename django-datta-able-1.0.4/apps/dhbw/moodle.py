# -*- coding: utf-8 -*-

"""the moodle module provides an interface to interact with moodle
"""

from typing import Any, ClassVar, Dict, List
from requests.models import Response
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from base import (
    Importer, MoodleCourseDict, MoodleModuleDict,
    reqget, reqpost, url_get_fqdn, url_get_args
)

###              ###
# HELPER FUNCTIONS #
###              ###

def add_to_module_dict(name: str, url: str) -> MoodleModuleDict:
    """function to fill a MoodleModuleDict with values and return it

    Parameters
    ----------
    name: str
        a name
    url: str
        an url

    Returns
    -------
    _: MoodleModuleDict
        a typed dictionary
    """
    return {
        "name": name,
        "url": url
    }

def get_bbb_instance_name(tag_a: Tag) -> str:
    """searches for the instance name for a given tag and returns it

    Parameters
    ----------
    tag_a: Tag
        the tag which contains the instance name

    Returns
    -------
    temp: str
        the instance name
    """
    temp: str
    tag_span: Tag
    for tag_span in tag_a.find_all("span"):
        if "instancename" in tag_span.get("class"):
            if len(tag_span.contents) == 1:
                temp = tag_span.string
            else:
                for content in tag_span.contents:
                    if isinstance(content, NavigableString):
                        temp = content.string
                        break
        break
    return temp

###                   ###
# MOODLE IMPORTER CLASS #
###                   ###

class MoodleImporter(Importer):
    """class to import data from moodle

    Attributes
    ----------
    __url: str
        the given url for moodle
    __logout_url: str
        the url for logout

    Methods
    -------
    login(self, username, password) : None
        creates a session for the user
    find_all_bbb_rooms(self, course_dict) : MoodleCourseDict
        find all bbb rooms and store them in the given dictionary
    scrape(self): None
        scrape for the website data
    logout(self): None
        removes the session and destroys the instance
    """

    __url: ClassVar[str] = "https://moodle.dhbw-mannheim.de/"
    __logout_url: str

    __slots__ = ("__logout_url",)

    def __init__(self) -> None:
        super().__init__()
        self.headers["Host"] = url_get_fqdn(MoodleImporter.__url)

    def login(self, username, password) -> None:
        """aquire the authentication token

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
        if "@" in username:
            username = username.split("@")[0]

        url: str = MoodleImporter.__url

        # get token from login page
        r_token: Response = reqget(url=url+"login/index.php", headers=self.headers)

        # extract the token from response
        self.headers["Cookie"] = r_token.headers["Set-Cookie"].split(";")[0]
        self.headers["Referer"] = url + "login/index.php"
        self.headers["Origin"] = url
        content_token: BeautifulSoup = BeautifulSoup(r_token.text, "lxml")
        tag_list: List[Tag] = content_token.find(id="login").find_all("input")
        elem: Tag
        for elem in tag_list:
            if elem.get("name") == "logintoken":
                logintoken: str = elem.get("value")
                break

        # set form data
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload: Dict[str, str] = {
            "anchor": "",
            "logintoken": logintoken,
            "username": username,
            "password": password
        }

        # post request for login
        r_login: Response = reqpost(
            url=url+"login/index.php",
            headers=self.headers,
            payload=payload,
            return_code=303
        )

        # add authentication cookie to the headers
        self.auth_token = r_login.headers["Set-Cookie"].split(";")[0]
        self.headers["Cookie"] = self.auth_token

        # drop content-type header
        self.drop_header("Content-Type")
        self.drop_header("Origin")

    def find_all_bbb_rooms(self, course_dict: MoodleCourseDict) -> MoodleCourseDict:
        """method to find all bbc rooms for a given course

        Attributes
        ----------
        course_dict: MoodleCourseDict
            a typed dictionary

        Returns
        -------
        course_dict: MoodleCourseDict
            a typed dictionary
        """
        r_course: Response = reqget(url=course_dict["href"], headers=self.headers)
        content_course: BeautifulSoup = BeautifulSoup(r_course.text, "lxml")

        tag_a: Tag
        for tag_a in content_course.find_all("a"):
            # in case there is an <a> without href as attribute
            if not tag_a.get("href"):
                continue
            temp_href: str = tag_a.get("href")
            if "bigbluebuttonbn" in temp_href:
                course_dict["bbb_rooms"].append(
                    add_to_module_dict(get_bbb_instance_name(tag_a), temp_href)
                )
        return course_dict

    def scrape(self) -> None:
        """scrape the wanted data from the website

        Returns
        -------
        None
        """
        url = MoodleImporter.__url

        # renew referer header
        self.headers["Referer"] = url

        # get profile data
        r_profile: Response = reqget(
            url=url+"user/profile.php",
            headers=self.headers
        )

        # parse html content of the response
        content_profile: BeautifulSoup = BeautifulSoup(r_profile.text, "lxml")

        # scrape username
        self.scraped_data["username"] = content_profile.find(id="usermenu").get("title")

        # scrape logout url
        tag_list: Tag = content_profile.find(id="usermenu-dropdown").find_all("a")
        for elem in tag_list:
            if elem.get("title") == "Logout":
                self.__logout_url = elem.get("href")

        # scrape for every joined course
        courses_dict: List[MoodleCourseDict] = []
        tag_list =  content_profile.find(id="adaptable-tab-coursedetails").find_all("a")
        argument: Any
        for elem in tag_list:
            for argument in url_get_args(elem.get("href")):
                if "id" in argument:
                    course_id: str = elem.split("=")[1]
                    break
            courses_dict.append(
                {
                    "name": argument.string,
                    "href": url+"course/view.php?id="+course_id,
                    "bbb_rooms": []
                }
            )

        # find every bbb room under the joined courses
        for course_dict in courses_dict:
            course_dict = self.find_all_bbb_rooms(course_dict)

        self.scraped_data["courses"] = courses_dict

    def logout(self) -> None:
        """sends a logout request and deletes the instance

        Returns
        -------
        None
        """
        # logout request
        reqget(url=self.__logout_url, headers=self.headers, return_code=303)

        # delete instance
        del self
