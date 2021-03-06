# -*- coding: utf-8 -*-

"""the zimbra module provides an interface to interact with zimbra
"""

import re
import json

from bs4 import BeautifulSoup

from dhbw.util import ImporterSession, reqget, reqpost, url_get_fqdn
from dhbw.util import ServiceUnavailableException, LoginRequiredException

#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

def _entity_list(in_list, out_list, in_type):
    """Adds entities to a list while converting an entity string to a dict.

    Parameters
    ----------
    in_list : List[str]
        Description
    out_list : List[Dict[str, str]]
        Description
    in_type : str
        Description
    Returns
    -------
    List[Dict[str, str]]

    """

    if in_type == "recipient":
        temp = "t"
    elif in_type == "cc":
        temp = "c"
    else:
        temp = "b"

    for account in in_list:
        temp_dict = {}
        temp_dict["t"] = temp
        temp_dict["a"] = account
        out_list.insert(0, temp_dict)

    return out_list


def _fill_contacts_dict_elem(contact):
    """Checks for existing keys inside the response contact dict and creates contact dict.

    Parameters
    ----------
    contact : Dict[str, str]

    Returns
    -------
    Dict

    """
    temp = {}
    if "email" in contact.keys():
        temp["email"] = contact["email"]
        temp["id"] = contact["id"]
        temp["firstName"] = None
        temp["lastName"] = None
        temp["jobTitle"] = None
        if "firstName" in contact.keys():
            temp["firstName"] = contact["firstName"]
        if "lastName" in contact.keys():
            temp["lastName"] = contact["lastName"]
        if "jobTitle" in contact.keys():
            temp["jobTitle"] = contact["jobTitle"]

    return temp

#------------------------------------------------------------------------------#
# Z I M B R A - H A N D L E R
#------------------------------------------------------------------------------#

class ZimbraHandler(ImporterSession):
    """Handler for interacting with zimbra.

    Attributes
    ----------
    url : str
        the given url for zimbra
    accountname : str
        the dhbw mail account
    contacts : List[Dict[str, str]]
        a list representing all contacts from zimbra
    realname : str
        the real name of the logged in user
    signatures : List[str]
        a list of all available signatures to the user

    Methods
    -------
    login(self): None
        creates a session for the user
    logout(self): None
        sends a logout request
    scrape(self): None
        scrape the wanted data from the website
    get_contacts(self): None
        import contacts from the default "contact" book
    new_contact(self, contact_dict): None
        create a new contact inside the default contact book
    remove_contact(self, contact_id): None
        remove an existing contact from the default contact book
    _create_entities_list(self, recipients, rec_cc, rec_bcc): List[Dict[str, str]]
        create a list with dictionary elements
    _generate_mail(self, mail_dict): Dict[str, Any]
        build the mail in the needed format for zimbra
    send_mail(self, mail_dict): None
        sends a mail to the soap backend of zimbra
    """

    url = "https://studgate.dhbw-mannheim.de/zimbra/"

    __slots__ = ("accountname", "contacts", "realname", "signatures",)

    def __init__(self):
        super().__init__()
        self.accountname = ""
        self.contacts = []
        self.headers["Host"] = url_get_fqdn(ZimbraHandler.url)
        self.realname = ""
        self.signatures = []

    async def login(self, username, password):
        """Authenticate the user against zimbra.

        Parameters
        ----------
            username: str
                the username for the authentication process
            password: str
                the password for the authentication process

        Returns
        -------
        ZimbraHandler
        """
        url = ZimbraHandler.url

        # add accountname
        self.accountname = username

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
        try:
            r_login = reqpost(
                url=url,
                headers=self.headers,
                payload=payload,
                allow_redirects=False,
                return_code=302
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        finally:
            # drop content-type header
            self.drop_header("Content-Type")

        # add authentication cookie to the headers
        self.auth_token = r_login.headers["Set-Cookie"].split(";")[0]
        self.headers["Cookie"] = self.headers["Cookie"] + "; " + self.auth_token

        return self

    async def scrape(self):
        # TODO documentation?
        """Scrape the selected data from zimbra.

        Returns
        -------
        None
        """
        url = ZimbraHandler.url

        try:
            r_home = reqget(
                url=url,
                headers=self.headers,
            )
        except ServiceUnavailableException as service_err:
            raise service_err

        content_home = BeautifulSoup(r_home.text, "lxml")

        # improvement idea -> let it loop reversed, since needed content
        #                     is inside the last / one of the last script tag(s)
        try:
            tag_script_all = content_home.find_all("script")
        except AttributeError as attr_err:
            raise LoginRequiredException() from attr_err

        for tag_script in tag_script_all:
            if "var batchInfoResponse" in str(tag_script.string):
                temp = re.search(
                    r"var\ batchInfoResponse\ =\ \{\"Header\":.*\"_jsns\":\"urn:zimbraSoap\"\};",
                    str(tag_script.string)
                )
                break
        temp_json = json.loads(
            re.sub(r"(var\ batchInfoResponse\ =\ )|(;$)", "", temp.group(0))
        )

        self.realname = temp_json["Body"]["BatchResponse"]["GetInfoResponse"][0]["attrs"]["_attrs"]["cn"]

        self.scraped_data = temp_json

    def get_contacts(self):
        """Import contacts from the default contact book.

        Returns
        -------
        None
        """
        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        # TODO query is limited to 100 contact entities --> query all contact entities

        query = {
            "Header": {
                "context": {
                    "_jsns": "urn:zimbra",
                    "account": {
                        "_content": self.accountname,
                        "by": "name"
                    }
                }
            },
            "Body": {
                "SearchRequest": {
                    "_jsns": "urn:zimbraMail",
                    "sortBy": "nameAsc",
                    "offset": 0,
                    "limit": 100,
                    "query": "in:contacts",
                    "types": "contact"
                }
            }
        }

        try:
            r_contacts = reqpost(
                url=origin + "/service/soap/SearchRequest",
                headers=self.headers,
                payload=json.dumps(query)
            ).json()
        except ServiceUnavailableException as service_err:
            raise service_err
        finally:
            self.drop_header("Content-Type")

        try:
            contacts = r_contacts["Body"]["SearchResponse"]["cn"]
        except KeyError:
            contacts = []

        for contact in contacts:
            cnt = contact["_attrs"]
            cnt["id"] = contact["id"]
            temp = _fill_contacts_dict_elem(cnt)
            if temp:
                self.contacts.append(temp)

    def new_contact(self, contact_dict):
        """Create a new contact inside the default contact book.

        Parameters
        ----------
        contact_dict : Dict

        Returns
        -------
        None
        """
        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        contact_details = []
        for key, value in contact_dict.items():
            if value:
                contact_details.append(
                    {
                        "n": key,
                        "_content": value
                    }
                )

        contact = {
            "Header": {
                "context": {
                    "_jsns": "urn:zimbra",
                    "account": {
                        "_content": self.accountname,
                        "by": "name"
                    },
                    "auth_token": self.auth_token
                }
            },
            "Body": {
                "CreateContactRequest": {
                    "_jsns": "urn:zimbraMail",
                    "cn": {
                        "l": "7",
                        "a": contact_details
                    }
                }
            }
        }

        try:
            r_contact = reqpost(
                url=origin + "/service/soap/CreateContactRequest",
                headers=self.headers,
                payload=json.dumps(contact),
            ).json()
        except ServiceUnavailableException as service_err:
            raise service_err
        finally:
            self.drop_header("Content-Type")

        try:
            contact_dict["id"] = r_contact["Body"]["CreateContactResponse"]["cn"][0]["id"]
        except AttributeError as attr_err:
            raise LoginRequiredException() from attr_err

        self.contacts.append(contact_dict)

    def remove_contact(self, contact_id):
        """remove an existing contact from the default contact book

        Parameters
        ----------
        contact_id : str

        """
        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        del_contact = {
            "Header": {
                "context": {
                    "_jsns": "urn:zimbra",
                    "account": {
                        "_content": self.accountname,
                        "by": "name"
                    },
                    "auth_token": self.auth_token
                }
            },
            "Body": {
                "ContactActionRequest": {
                    "_jsns": "urn:zimbraMail",
                    "action": {
                        "id": contact_id,
                        "l": "3",
                        "op": "move"
                    }
                }
            }
        }

        try:
            reqpost(
                url=origin + "/service/soap/ContactActionRequest",
                headers=self.headers,
                payload=json.dumps(del_contact)
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        finally:
            self.drop_header("Content-Type")

        i = 0
        while i < len(self.contacts):
            if self.contacts[i]["id"] == contact_id:
                break
            i += 1

        del self.contacts[i]

    def _create_entities_list(self, recipients, rec_cc, rec_bcc):
        """Create a list with dictionary elements.

        Parameters
        ----------
        recipients : List[str]

        rec_cc : List[str]

        rec_bcc : List[str]


        Returns
        -------
        List[Dict[str, str]]
        """
        entities_list = [
            {
                "t": "f",
                "a": self.accountname,
                "p": self.realname
            }
        ]

        entities_list = _entity_list(rec_bcc, entities_list, "bcc")
        entities_list = _entity_list(rec_cc, entities_list, "cc")
        entities_list = _entity_list(recipients, entities_list, "recipient")

        return entities_list

    def _generate_mail(self, mail_dict):
        """build the mail in the needed format for zimbra

        Parameters
        ----------
        mail_dict : Dict

        Returns
        -------
        Dict[str, Any]
        """
        header_dict = {
            "context": {
                "_jsns": "urn:zimbra",
                "account": {
                    "_content": self.accountname,
                    "by": "name"
                },
                "auth_token": self.auth_token
            }
        }

        entities = self._create_entities_list(
            mail_dict["recipients"],
            mail_dict["rec_cc"],
            mail_dict["rec_bcc"]
        )

        message_dict = {
            "_jsns": "urn:zimbraMail",
            "m": {
                "e": entities,
                "su": {
                    "_content": mail_dict["subject"]
                },
                "mp": {
                    "ct": mail_dict["cttype"],
                    "content": {
                        "_content": mail_dict["content"]
                    }
                }
            }
        }

        # join the dicts to create the whole mail
        mail = {
            "Header": header_dict,
            "Body": {
                "SendMsgRequest": message_dict
            }
        }

        return mail

    def send_mail(self, mail_dict):
        """Sends a mail to the soap backend of zimbra.

        Parameters
        ----------
        mail_dict: SendMailDict
            a dictionary containing recipients, subject, content-type and the actual content

        Returns
        -------
        None
        """
        # create mail
        mail = self._generate_mail(mail_dict)

        # IMPROVEMENT IDEA:
        # store mail_dict somewhere, in case that the service is unavailable

        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        try:
            reqpost(
                url=origin + "/service/soap/SendMsgRequest",
                headers=self.headers,
                payload=json.dumps(mail),
                return_code=200
            )
        except ServiceUnavailableException as service_err:
            raise service_err
        finally:
            self.drop_header("Content-Type")

    def logout(self):
        """sends a logout request

        Returns
        -------
        None
        """
        url = ZimbraHandler.url

        try:
            reqget(
                url=url,
                headers=self.headers,
                params={"loginOp": "logout"},
                return_code=200
            )
        except ServiceUnavailableException as service_err:
            raise service_err

        self.auth_token = ""
