# -*- coding: utf-8 -*-

"""the zimbra module provides an interface to interact with zimbra
"""

import re
import json
from bs4 import BeautifulSoup
from .util import ImporterSession, reqget, reqpost, url_get_fqdn

###            ###
# ZIMBRA HANDLER #
###            ###

class ZimbraHandler(ImporterSession):
    """handler for interacting with zimbra

    Attributes
    ----------
    url: str
        the given url for zimbra
    auth_token: str
        the string representing the authentication cookie for the created session
    headers: dict
        a dictionary with default headers and their respective values

    Methods
    -------
    drop_header(self, header) : None
        drop the given header from headers dict
    login(self) : None
        creates a session for the user
    """

    url = "https://studgate.dhbw-mannheim.de/zimbra/"

    __slots__ = ("contacts",)

    def __init__(self):
        super().__init__()
        self.headers["Host"] = url_get_fqdn(ZimbraHandler.url)
        self.contacts = {}

    def login(self, username, password):
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
        url = ZimbraHandler.url

        # set headers for post request
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Cookie"] = "ZM_TEST=true"

        # form data
        payload = {
            "client": "preferred",
            "loginOp": "login",
            "username": username,
            "password": password
        }

        # LOGIN - POST REQUEST
        r_login = reqpost(
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

    def structure_scraped_data(self):
        """
        """
        pass

    def scrape(self):
        """
        """
        url = ZimbraHandler.url

        r_home = reqget(
            url=url,
            headers=self.headers,
        )

        content_home = BeautifulSoup(r_home.text, "lxml")

        # improvement idea -> let it loop reversed, since needed content
        #                     is inside the last / one of the last script tag(s)
        for tag_script in content_home.find_all("script"):
            if "var batchInfoResponse" in str(tag_script.string):
                temp = re.search(
                    r"var\ batchInfoResponse\ =\ \{\"Header\":.*\"_jsns\":\"urn:zimbraSoap\"\};",
                    str(tag_script.string)
                )
                break
        temp_json = json.loads(
            re.sub(r"(var\ batchInfoResponse\ =\ )|(;$)", "", temp.group(0))
        )
        self.scraped_data = json.dumps(temp_json)

    def send_mail(self, ):
        """
        """
        url = ZimbraHandler.url

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url

        data = {
            "Header": {
                "context": {
                    "auth_token": self.auth_token
                }
            },
            "Body": {
                "SendMsgRequest": {
                    "m": {

                    }
                }
            }
        }

        r_send_mail = reqpost(
            url=url+"service/soap/SendMsgRequest",
            headers=self.headers,
            payload=json.dumps(data)
        )

    def logout(self):
        """
        """
        url = ZimbraHandler.url

        reqget(
            url=url,
            headers=self.headers,
            params={"loginOp": "logout"},
            return_code=200
        )
        self.auth_token = ""
