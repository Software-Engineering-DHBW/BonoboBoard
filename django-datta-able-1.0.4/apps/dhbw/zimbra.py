# -*- coding: utf-8 -*-

"""the zimbra module provides an interface to interact with zimbra
"""

from typing import ClassVar, Dict
from requests.models import Response
from base import reqpost, url_get_fqdn

###            ###
# ZIMBRA HANDLER #
###            ###

class ZimbraHandler:
    """handler for interacting with zimbra

    Attributes
    ----------
    __url: str
        the given url for zimbra
    __auth_token: str
        the string representing the authentication cookie for the created session
    __headers: dict
        a dictionary with default headers and their respective values

    Methods
    -------
    drop_header(self, header) : None
        drop the given header from headers dict
    login(self) : None
        creates a session for the user
    """

    __url: ClassVar[str] = "https://studgate.dhbw-mannheim.de/zimbra/"

    __auth_token: str
    __headers: Dict[str, str]

    __slots__ = ("__auth_token", "__headers")

    def __init__(self, username: str, password: str) -> None:
        usr_ag = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        self.__headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Host": url_get_fqdn(ZimbraHandler.__url),
            "User-Agent": usr_ag
        }
        self.login(username, password)

    @property
    def auth_token(self) -> str:
        """getter for attribute __auth_token"""
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, value: str) -> None:
        """setter for attribute __auth_token"""
        self.__auth_token = value

    @property
    def headers(self) -> Dict[str, str]:
        """getter for attribute __headers"""
        return self.__headers

    @headers.setter
    def headers(self, key: str, value: str) -> None:
        """setter for attribute __headers"""
        self.__headers[key] = value

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

    def login(self, username: str, password: str) -> None:
        """authenticate the user against zimbra

        Parameters
        ----------
            username: str
                the username for the authentication process
            password: str
                the password for the authentication process

        Returns
        -------
        None
        """
        url: str = ZimbraHandler.__url

        # set headers for post request
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Cookie"] = "ZM_TEST=true"

        # form data
        payload: Dict[str, str] = {
            "client": "preferred",
            "loginOp": "login",
            "username": username,
            "password": password
        }

        # LOGIN - POST REQUEST
        r_login: Response = reqpost(
            url=url,
            headers=self.headers,
            payload=payload,
            allow_redirects=False,
            return_code=302
        )

        # add authentication cookie to the headers
        self.auth_token = r_login.headers["Set-Cookie"].split(";")[0]
        self.headers["Cookie"] = self.headers["Cookie"] + "; " + self.auth_token

        # drop content-type header
        self.drop_header("Content-Type")

    # def scrape(self) -> None:
    #     """
    #     """
    #     # lazy peon
    #     url: str = ZimbraHandler.__url

    # def write_mail(self) -> None:
    #     """
    #     """
    #     # lazy peon
    #     url: str = ZimbraHandler.__url
