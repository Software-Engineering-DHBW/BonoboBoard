# -*- coding: utf-8 -*-

"""the base module provides basic functionality for requests
"""

from typing import Any, Dict, List, NoReturn, TypedDict, Union
import re
import requests
from requests.models import Response
from requests.exceptions import RequestException

###                ###
# TYPING DEFINITIONS #
###                ###

class MoodleModuleDict(TypedDict):
    """TypedDict for moodle course modules"""
    name: str
    url: str

class MoodleCourseDict(TypedDict):
    """TypedDict for moodle courses"""
    name: str
    href: str
    bbb_rooms: List[MoodleModuleDict]

MoodleDict = Dict[str, Union[List[MoodleCourseDict], str]]

###              ###
# HELPER FUNCTIONS #
###              ###

def reqpost(
        *, url: str = "", headers: Dict[str, str] = None,
        params: Dict[str, str] = None, payload: Dict[str, str] = None,
        allow_redirects: bool = False, return_code: int = 200) -> Union[Response, NoReturn]:
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

    res: Response = requests.post(
        url=url,
        headers=headers,
        params=params,
        data=payload,
        allow_redirects=allow_redirects
    )

    err_msg = f"return code: [{ res.status_code }]\nexpected return code: [{ return_code }]"

    # compare return code with expected return code
    if not res.status_code == return_code:
        raise RequestException(err_msg)
    return res

def reqget(
        *, url: str = "", headers: Dict[str, str] = None,
        params: Dict[str, str] = None, allow_redirects: bool = False,
        return_code: int = 200) -> Union[Response, NoReturn]:
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

    res: Response = requests.get(
        url=url,
        headers=headers,
        params=params,
        allow_redirects=allow_redirects
    )

    err_msg = f"return code: [{ res.status_code }]\nexpected return code: [{ return_code }]"

    # compare return code with expected return code
    if not res.status_code == return_code:
        raise RequestException(err_msg)
    return res

def url_get_fqdn(url: str) -> str:
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
    return re.sub(r"(^http[s]?://)|(/.*$)", "", url)

def url_get_path(url: str) -> str:
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
    return re.sub(r"(^.*/)|(\?.*$)", "", url)

def url_get_args(url: str) -> List[str]:
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
    return re.sub(r"^.*\?", "", url).split("&")

###                 ###
# ABSTRACT BASE CLASS #
###                 ###

class Importer:
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
    drop_header(self, header) : None
        method to drop an header
    """

    __auth_token: str
    __headers: Dict[str, str]
    __scraped_data: Dict[str, Union[MoodleDict, Any]]

    __slots__ = ("__auth_token", "__headers", "__scraped_data",)

    def __init__(self):
        usr_ag = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        self.__headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": usr_ag
        }

    @property
    def auth_token(self) -> str:
        """getter for attribute __auth_token"""
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, token) -> None:
        """setter for attribute __auth_token"""
        self.__auth_token = token

    @property
    def headers(self) -> Dict[str, str]:
        """getter for attribute __headers"""
        return self.__headers

    @headers.setter
    def headers(self, key, value) -> None:
        """"setter for attribute __headers"""
        self.__headers[key] = value

    @property
    def scraped_data(self) -> Dict[str, Union[MoodleDict, Any]]:
        """"getter for attribute __scraped_data"""
        return self.__scraped_data

    @scraped_data.setter
    def scraped_data(self, key: str, value: Union[MoodleDict, Any]) -> None:
        """setter for attribute __scraped_data"""
        self.__scraped_data[key] = value

    def drop_header(self, header) -> None:
        """method to drop an header

        Parameters
        ----------
        header: str
            the name of the header which should be dropped

        Returns
        -------
        None
        """
        self.__headers.pop(header)
