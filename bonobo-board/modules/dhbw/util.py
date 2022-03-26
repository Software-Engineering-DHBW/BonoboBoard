# -*- coding: utf-8 -*-

"""the util module provides basic functionality for requests
"""

from abc import ABC, ABCMeta, abstractmethod
import re
import requests
from requests.exceptions import RequestException

#------------------------------------------------------------------------------#
# C U S T O M - E R R O R - C L A S S E S
#------------------------------------------------------------------------------#

class ReturnCodeException(Exception):
    """Exception raised if the status code differs from the expected code.
    """
    def __init__(self, status_code, actual_return_code, msg=""):
        self.status_code = status_code
        self.return_code = actual_return_code
        if not msg:
            self.msg = (
                f"the returned STATUS CODE [{self.status_code}]"
                f"differs from the expected STATUS CODE [{self.return_code}]"
            )
        else:
            self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

class ServiceUnavailableException(Exception):
    """Exception raised if no connection to the service could be established.
    """
    def __init__(self, msg="Service gerade nicht verfügbar!"):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

class CredentialsException(Exception):
    """Exception raised if the credentials are wrong
    """
    def __init__(self, msg="Falsche Eingabedaten!"):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

class LoginRequiredException(Exception):
    """Exception raised if accessing a protected resource, which requires an
    authentication process.
    """
    def __init__(self, msg="Resource is only accessable through authentication!"):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}"

#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

def reqpost(
        *, url="", headers=None,
        params=None, payload=None,
        allow_redirects=False, return_code=200):
    """Wrapper for a post request with return code check.

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
    try:
        res = requests.post(
            url=url,
            headers=headers,
            params=params,
            data=payload,
            allow_redirects=allow_redirects
        )

        # compare return code with expected return code
        if not res.status_code == return_code:
            raise ReturnCodeException(res.status_code, return_code)
    except RequestException as req_err:
        raise ServiceUnavailableException() from req_err
    except ReturnCodeException as ret_err:
        raise ServiceUnavailableException() from ret_err
    return res

def reqget(
        *, url="", headers=None,
        params=None, allow_redirects=False,
        return_code=200):
    """Wrapper for a get request with return code check.

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
    try:
        res = requests.get(
            url=url,
            headers=headers,
            params=params,
            allow_redirects=allow_redirects
        )

        # compare return code with expected return code
        if not res.status_code == return_code:
            raise ReturnCodeException(res.status_code, return_code)
    except RequestException as req_err:
        raise ServiceUnavailableException() from req_err
    except ReturnCodeException as ret_err:
        raise ServiceUnavailableException() from ret_err
    return res

def url_get_fqdn(url):
    """Return FQDN of the provided url.

    Parameters
    ----------
    url : str
        the url from which the fqdn should be extracted

    Returns
    -------
    _ : str
        the FQDN of the given url
    """
    return re.sub(r"(^http[s]?://)|(/.*$)", "", url)


def url_get_path(url):
    """return path to file of the provided url

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
    """return array of arguments of the provided url

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

#------------------------------------------------------------------------------#
# B A S E - C L A S S E S
#------------------------------------------------------------------------------#

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
    """Base class for every importer with session handling.

    Attributes
    ----------
    auth_token: str
        the string representing the authentication cookie for the created session
    email: str
        the email of the current user
    """

    __slots__ = ("auth_token", "email",)

    def __init__(self):
        super().__init__()
        self.auth_token = ""
        self.email = ""

    @abstractmethod
    async def login(self, username, password):
        pass

    @abstractmethod
    async def scrape(self):
        pass

    @abstractmethod
    def logout(self):
        pass
