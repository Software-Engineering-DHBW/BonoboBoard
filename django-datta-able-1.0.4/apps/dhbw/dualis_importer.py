# -*- coding: utf-8 -*-

"""
"""

import sys
import re
from bs4 import BeautifulSoup
import pandas as pd
from util import *


def parse_html(html_data):
    print("HTML-Parser")

    table_mn = pd.read_html(html_data)

    df = table_mn[0]
    grades = {}
    for ind in df.index:

        subject = df['Unnamed: 1'].loc[ind]
        subject = re.sub("(<!--.*$|[\n\r])*", "", subject)
        module = df['Unnamed: 0'].loc[ind]

        if module != "Gesamt-GPA" and len(module) > 10 or module == "Module":    # Skip "Summe Informationstechnik" or stuff like that. Better idea?
            continue

        grades[str(ind)] = {
            "modul": module,
            "subject": subject.strip(),
            "grade": df['Note'].loc[ind],
            "credits": df['Credits'].loc[ind],
            "status": df['Status'].loc[ind],
            "date": df['Datum'].loc[ind]
        }

    grades["GPA"] = {
            "total_gpa_grade": table_mn[1].columns.values.tolist()[- 1][0],
            "major_subject_gpa_grade": table_mn[1].columns.values.tolist()[- 1][1]
        }

    print(grades)


class DualisImporter(Importer):
    """
    """

    url = "https://dualis.dhbw.de/scripts/mgrqispi.dll"
    __auth_token: str

    def __init__(self, user, passwd):
        super().__init__()
        print("dualisImporter init")
        self.__auth_token = ""
        # set default headers
        self.headers["Host"] = url_get_fqdn(DualisImporter.url)
        # TODO HERE CHECK IF SERVER UP / DOWN --> SIMPLE GET REQUEST

        # --- CALL METHODS ---
        r_dict =  self.login(user,passwd)
        self.headers["Cookie"] = r_dict["cookie"]
        args = r_dict["arguments"]
        htmlResult = self.query_data(args)
        parse_html(htmlResult)
        # self.logout(args)

    def login(self, username, password):
        """acquire the authentication token

        Parameters
        ----------
        username: str
            username used to log in
        password: str
            password used to log in

        Returns
        -------
        None
        """

        url = DualisImporter.url

        # prepare for login
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = {
            "APPNAME": "CampusNet",
            "PRGNAME": "LOGINCHECK",
            "ARGUMENTS": "clino,usrname,pass,menuno,menu_type,browser,platform",
            "clino": "000000000000001",
            "menuno": "000324",
            "menu_type": "classic",
            "browser": "",
            "platform": "",
            "usrname": username,
            "pass": password
        }

        # send login request
        r = reqpost(
            url=url,
            headers=self.headers,
            payload=data,
            return_code=200
        )

        # pop Content-Type from headers --> just needed for post calls
        self.drop_header("Content-Type")

        # check if response is faulty
        if not r.status_code == 200:
            # TODO ERROR --> LOGGER
            print("Something went wrong while trying to login\n!", sys.stderr)

        # filter response for needed data
        arg_string = re.sub(
            "(^.*URL=)", "", r.headers["REFRESH"]).split("?")[1]
        arg_string = arg_string.split("&")
        arg_dict = {}
        for arg in arg_string:
            _arg = arg.split("=")
            arg_dict[_arg[0]] = _arg[1]

        # change PRGNAME from STARTPAGE_DISPATCH to MLSSTART
        arg_dict["PRGNAME"] = "MLSSTART"
        # remove last entry from ARGUMENTS (-N000000000000000)
        arg_dict["ARGUMENTS"] = arg_dict["ARGUMENTS"].split(",")[:2]

        # return object with needed data
        ret_dict = {
            "cookie": re.sub("[\s]|(;.*)", "", r.headers["Set-cookie"]),
            "arguments": arg_dict
        }

        # return
        return ret_dict

    def query_data(self, args):
        """
        """

        url = DualisImporter.url

        # send request
        r = reqget(
            url=url,
            headers=self.headers,
            params=args
        )

        if not r.status_code == 200:
            # TODO ERROR --> LOGGER
            print("Something went wrong while trying to query the data\n!", sys.stderr)
        # TODO DEBUG --> LOGGER
        print(f"Status Code: { r.status_code }\nHeaders:\n{ r.headers }\n\n", sys.stdout)

        # parse html content to work on it (1)
        # =========
        # WIP START
        html = BeautifulSoup(r.text, "lxml")
        # First Approach
        leistung_url_1 = html.find(id="link000310").a.get("href")
        # Second Approach
        for link in html.find_all("a"):
            if link.string == "LeistungsÃ¼bersicht":
                leistung_url_2 = link.get("href")

        # WIP END
        # =======

        # filter response for needed data
        l_arg_string = leistung_url_1.split(
            "?")[1]  # HERE CHOOSE BETWEEN APPROACHES
        l_arg_string = l_arg_string.split("&")
        l_arg_dict = {}
        for l_arg in l_arg_string:
            l_arg = l_arg.split("=")
            l_arg_dict[l_arg[0]] = l_arg[1]

        # change PRGNAME from STARTPAGE_DISPATCH to MLSSTART
        l_arg_dict["PRGNAME"] = "STUDENT_RESULT"

        r_leistung = reqget(
            url=url,
            headers=self.headers,
            params=l_arg_dict
        )

        return r_leistung.text

    def logout(self, args):
        """sends a logout request

        Returns
        -------
        None
        """

        # change PRGNAME to LOGOUT
        args["PRGNAME"] = "LOGOUT"

        r = reqget(
            url=DualisImporter.__url,
            headers=self.headers,
            params=args
        )
