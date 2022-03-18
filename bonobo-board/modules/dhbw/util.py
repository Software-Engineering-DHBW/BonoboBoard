# -*- coding: utf-8 -*-

"""the util module provides basic functionality for requests
"""

from abc import ABC, ABCMeta, abstractmethod
import re
import requests
from requests.exceptions import RequestException

###              ###
# HELPER FUNCTIONS #
###              ###

def reqpost(
        *, url = "", headers = None,
        params = None, payload = None,
        allow_redirects = False, return_code = 200):
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

    res = requests.post(
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
        *, url = "", headers = None,
        params = None, allow_redirects = False,
        return_code = 200):
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

    res = requests.get(
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
    return re.sub(r"(^http[s]?://)|(/.*$)", "", url)

def url_get_path(url):
    """return path to file of an url

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
    return re.sub(r"^.*\?", "", url).split("&")

###                 ###
# ABSTRACT BASE CLASS #
###                 ###

class Importer(ABC):
    """base class for every importer

    Attributes
    ----------
    headers: dict
        a dictionary with default headers and their respective values
    scraped_data: dict
        a dictionary representing the scraped data

    Methods
    -------
    drop_header(self, header) : None
        method to drop an header
    """

    __slots__ = ("headers", "scraped_data",)

    def __init__(self):
        usr_ag = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": usr_ag
        }
        self.scraped_data = {}

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
        self.headers.pop(header)

class ImporterSession(Importer, metaclass=ABCMeta):
    """base class for every importer with session handling

    Attributes
    ----------
    auth_token : str
        the string representing the authentication cookie for the created session
    """

    __slots__ = ("auth_token","email",)

    def __init__(self):
        super().__init__()
        self.auth_token = ""
        self.email = ""

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def logout(self):
        pass
