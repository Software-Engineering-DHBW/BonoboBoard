# -*- coding: utf-8 -*-

"""the zimbra module provides an interface to interact with zimbra
"""

import re
import json

from bs4 import BeautifulSoup

from dhbw.util import ImporterSession, reqget, reqpost, url_get_fqdn

def _entity_list(in_list, out_list, in_type):
    """adds entities to a list while converting an entity string to a dict"""
    temp = ""
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
    """checks for existing keys inside the response contact dict and creates contact dict"""
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

###            ###
# ZIMBRA HANDLER #
###            ###

class ZimbraHandler(ImporterSession):
    """handler for interacting with zimbra

    Attributes
    ----------
    url: str
        the given url for zimbra
    accountname: str
        the dhbw mail account
    contacts: List[Dict[str, str]]
        a list representing all contacts from zimbra
    realname: str
        the real name of the logged in user
    signatures: List[str]
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
        """authenticate the user against zimbra

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

        self.email = username

        return self

    async def scrape(self):
        """scrape the wanted data from the website

        Returns
        -------
        None
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

        self.realname = temp_json["Body"]["BatchResponse"]["GetInfoResponse"][0]["attrs"]["_attrs"]["cn"]

        self.scraped_data = temp_json

    def get_contacts(self):
        """import contacts from the default contact book

        Returns
        -------
        None
        """
        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        #TODO query is limited to 100 contact entities --> query all contact entities

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
                    "offset":  0,
                    "limit": 100,
                    "query": "in:contacts",
                    "types": "contact"
                }
            }
        }

        r_contacts = reqpost(
            url=origin+"/service/soap/SearchRequest",
            headers=self.headers,
            payload=json.dumps(query)
        ).json()

        for contact in r_contacts["Body"]["SearchResponse"]["cn"]:
            cn = contact["_attrs"]
            cn["id"] = contact["id"]
            temp = _fill_contacts_dict_elem(cn)
            if temp:
                self.contacts.append(temp)

    def new_contact(self, contact_dict):
        """create a new contact inside the default contact book"""
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
                    "_jsns":"urn:zimbra",
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

        r_contact = reqpost(
            url=origin+"/service/soap/CreateContactRequest",
            headers=self.headers,
            payload=json.dumps(contact),
        ).json()

        self.drop_header("Content-Type")
        contact_dict["id"] = r_contact["Body"]["CreateContactResponse"]["cn"][0]["id"]
        self.contacts.append(contact_dict)

    def remove_contact(self, contact_id):
        """remove an existing contact from the default contact book"""
        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        del_contact = {
            "Header": {
                "context": {
                    "_jsns":"urn:zimbra",
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

        reqpost(
            url=origin+"/service/soap/ContactActionRequest",
            headers=self.headers,
            payload=json.dumps(del_contact)
        )

        self.drop_header("Content-Type")

        i = 0
        while i < len(self.contacts):
            if self.contacts[i]["id"] == contact_id:
                break
            i+=1

        del self.contacts[i]

    def _create_entities_list(self, recipients, rec_cc, rec_bcc):
        """create a list with dictionary elements"""
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

        return  entities_list

    def _generate_mail(self, mail_dict):
        """build the mail in the needed format for zimbra"""
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
        """sends a mail to the soap backend of zimbra
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

        url = ZimbraHandler.url
        origin = "https://" + url_get_fqdn(url)

        self.headers["Content-Type"] = "application/soap+xml; charset=utf-8"
        self.headers["Referer"] = url
        self.headers["Origin"] = origin

        reqpost(
            url=origin+"/service/soap/SendMsgRequest",
            headers=self.headers,
            payload=json.dumps(mail),
            return_code=200
        )

        self.drop_header("Content-Type")

    def logout(self):
        """sends a logout request

        Returns
        -------
        None
        """
        url = ZimbraHandler.url

        reqget(
            url=url,
            headers=self.headers,
            params={"loginOp": "logout"},
            return_code=200
        )
        self.auth_token = ""
