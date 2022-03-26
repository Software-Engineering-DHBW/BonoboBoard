# -*- coding: utf-8 -*-

"""the moodle module provides an interface to interact with moodle
"""

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from .util import ImporterSession, reqget, reqpost, url_get_fqdn, url_get_args
from .util import (
    CredentialsException, LoginRequiredException, ServiceUnavailableException
)

#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

def add_to_module_dict(name, url):
    """Function to fill a MoodleModuleDict with values and return it.

    Parameters
    ----------
    name: str
        Name of module
    url: str


    Returns
    -------
    _: MoodleModuleDict
        a typed dictionary
    """
    return {
        "name": name,
        "url": url
    }


def get_bbb_instance_name(tag_a):
    """Searches for the instance name for a given tag and returns it.

    Parameters
    ----------
    tag_a: Tag
        the tag which contains the instance name

    Returns
    -------
    temp: str
        the instance name
    """
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

#------------------------------------------------------------------------------#
# M O O D L E - I M P O R T E R
#------------------------------------------------------------------------------#

class MoodleImporter(ImporterSession):
    """Class to import data from moodle.

    Attributes
    ----------
    url: str
        The given url for moodle.
    logout_url: str
        The url for logout.

    Methods
    -------
    login(self, username, password): None
        creates a session for the user
    find_all_bbb_rooms(self, course_dict): MoodleCourseDict
        find all bbb rooms and store them in the given dictionary
    scrape(self): None
        scrape moodle data
    logout(self): None
        sends the logout request
    """

    url = "https://moodle.dhbw-mannheim.de/"

    __slots__ = ("logout_url",)

    def __init__(self):
        super().__init__()
        self.headers["Host"] = url_get_fqdn(MoodleImporter.url)
        self.logout_url = ""

    async def login(self, username, password):
        """Acquire the authentication token.

        Parameters
        ----------
        username: str
            username used to login
        password: str
            password used to login

        Returns
        -------
        MoodleImporter
        """
        if "@" in username:
            username = username.split("@")[0]

        url = MoodleImporter.url

        # get token from login page
        try:
            r_token = reqget(url=url + "login/index.php", headers=self.headers)
        except ServiceUnavailableException as service_err:
            raise service_err

        # extract the token from response
        self.headers["Cookie"] = r_token.headers["Set-Cookie"].split(";")[0]
        self.headers["Referer"] = url + "login/index.php"
        self.headers["Origin"] = url
        content_token = BeautifulSoup(r_token.text, "lxml")
        tag_list = content_token.find(id="login").find_all("input")
        for elem in tag_list:
            if elem.get("name") == "logintoken":
                logintoken: str = elem.get("value")
                break

        # set form data
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "anchor": "",
            "logintoken": logintoken,
            "username": username,
            "password": password
        }

        # post request for login
        try:
            r_login = reqpost(
                url=url + "login/index.php",
                headers=self.headers,
                payload=payload,
                return_code=303
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        except CredentialsException as cred_err:
            raise cred_err
        finally:
            self.drop_header("Content-Type")
            self.drop_header("Origin")

        # add authentication cookie to the headers
        self.auth_token = r_login.headers["Set-Cookie"].split(";")[0]
        self.headers["Cookie"] = self.auth_token

        self.email = username

        return self

    def find_all_bbb_rooms(self, course_dict):
        """Method to find all bbc rooms for a given course.

        Attributes
        ----------
        course_dict: MoodleCourseDict
            a typed dictionary

        Returns
        -------
        course_dict: MoodleCourseDict
            a typed dictionary
        """
        try:
            r_course = reqget(
                url=course_dict["href"],
                headers=self.headers)
        except ServiceUnavailableException as service_err:
            raise service_err

        content_course = BeautifulSoup(r_course.text, "lxml")

        try:
            tag_a_list = content_course.find_all("a")
        except AttributeError as attr_err:
            raise LoginRequiredException from attr_err

        for tag_a in tag_a_list:
            # in case there is an <a> without href as attribute
            if not tag_a.get("href"):
                continue
            temp_href = tag_a.get("href")
            if "bigbluebuttonbn" in temp_href:
                course_dict["bbb_rooms"].append(
                    add_to_module_dict(get_bbb_instance_name(tag_a), temp_href)
                )

        return course_dict

    async def scrape(self):
        """Scrape selected data from moodle.

        Returns
        -------
        None
        """

        url = MoodleImporter.url

        # renew referer header
        self.headers["Referer"] = url

        # get profile data
        try:
            r_profile = reqget(
                url=url + "user/profile.php",
                headers=self.headers
            )
        except ServiceUnavailableException as service_err:
            raise service_err

        # parse html content of the response
        content_profile = BeautifulSoup(r_profile.text, "lxml")

        # scrape username
        try:
            self.scraped_data["username"] = content_profile.find(id="usermenu").get("title")
        except AttributeError as attr_err:
            raise LoginRequiredException() from attr_err

        # scrape logout url
        try:
            tag_list = content_profile.find(id="usermenu-dropdown").find_all("a")
        except AttributeError as attr_err:
            raise LoginRequiredException() from attr_err

        for elem in tag_list:
            if elem.get("title") == "Logout":
                self.logout_url = str(elem.get("href"))

        # scrape for every joined course
        courses_dict = []

        try:
            tag_list = content_profile.find(id="adaptable-tab-coursedetails").find_all("a")
        except AttributeError as attr_err:
            raise LoginRequiredException() from attr_err

        for elem in tag_list:
            for argument in url_get_args(elem.get("href")):
                if "course" in argument:
                    course_id = argument.split("=")[1]
                    break
            courses_dict.append(
                {
                    "name": elem.string,
                    "href": url + "course/view.php?id=" + course_id,
                    "bbb_rooms": []
                }
            )

        # find every bbb room under the joined courses
        for course_dict in courses_dict:
            try:
                course_dict = self.find_all_bbb_rooms(course_dict)
            except ServiceUnavailableException as service_err:
                raise service_err
            except LoginRequiredException as log_req_err:
                raise log_req_err

        self.scraped_data["courses"] = courses_dict

    def logout(self):
        """Sends a logout request.

        Returns
        -------
        None
        """
        # logout request
        try:
            reqget(
                url=self.logout_url,
                headers=self.headers,
                return_code=303
            )
        except ServiceUnavailableException as service_err:
            raise service_err

        self.auth_token = ""
