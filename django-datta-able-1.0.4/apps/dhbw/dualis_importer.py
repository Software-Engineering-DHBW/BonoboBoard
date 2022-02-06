# -*- coding: utf-8 -*-

"""
"""

from email import header
import sys
import re
from bs4 import BeautifulSoup
import pandas as pd
from util import *


class DualisImporter(Importer):
    """
    """
    __url = "https://dualis.dhbw.de/scripts/mgrqispi.dll"
    __auth_token: str

    def __init__(self, user, passwd):
        super().__init__()
        print("dualisImporter init")
        self.__auth_token = ""
        # set default headers
        self.headers["Host"] = url_get_fqdn(DualisImporter.__url)
        # TODO HERE CHECK IF SERVER UP / DOWN --> SIMPLE GET REQUEST

        # --- CALL METHODS ---
        r_dict =  self.login(user,passwd)
        self.headers["Cookie"] = r_dict["cookie"]
        args = r_dict["arguments"]
        htmlResult = self.query_data(args)
        # self.parse_HTML(htmlResult)
        self.parse_HTML(htmlResult)
        # self.logout(args)

    def login(self, user, passwd):
        """
        """
        print("login")
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
            "usrname": user,
            "pass": passwd
        }

        # send login request
        r = reqpost(url=DualisImporter.__url, headers=self.headers, payload=data, return_code=200)

        # pop Content-Type from headers --> just needed for post calls
        self.drop_header("Content-Type")

        # check if response is faulty
        if not r.status_code == 200:
            # TODO ERROR --> LOGGER
            print("Something went wrong while trying to login\n!", sys.stderr)

        # filter response for needed data
        # format: "REFRESH': '0; URL=/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=STARTPAGE_DISPATCH&ARGUMENTS=-N751888937367774,-N000019,-N000000000000000"
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

        # TODO DEBUG --> LOGGER
        print(f"COOKIE & ARGUMENTS\n{ ret_dict}", sys.stdout)

        # return
        return ret_dict

    def query_data(self, args):
        """
        """
        print("query_data")
        # send request
        r = reqget(url=DualisImporter.__url, headers=self.headers, params=args)
        if not r.status_code == 200:
            # TODO ERROR --> LOGGER
            print("Something went wrong while trying to query the data\n!", sys.stderr)
        # TODO DEBUG --> LOGGER
        print(
            f"Status Code: { r.status_code }\nHeaders:\n{ r.headers }\n\n", sys.stdout)
        #print(f"=== RAW CONTENT ===\n{ r.text }", sys.stdout)

        # parse html content to work on it (1)
        # =========
        # WIP START
        html = BeautifulSoup(r.text, "lxml")
        # TODO DEBUG --> LOGGER
        #print(f"HTML BEAUTIFUL\n{ html }", sys.stdout)
        print("===\n===\n===\n")
        # First Approach
        #pruefung_url_1 = html.find(id="link000307").get("href")
        leistung_url_1 = html.find(id="link000310").a.get("href")
        print("===\n===\n===\n")
        print("===\n===\n===\n")
        # print(f"{leistung_url_1}")
        # Second Approach
        for link in html.find_all("a"):
            if link.string == "LeistungsÃ¼bersicht":
                leistung_url_2 = link.get("href")
            # if link.string == "PrÃ¼fungsergebnisse":
            #    pruefung_url_2 = link.get("href")

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

        #r_pruefung = req(url=pruefung_url_1, headers=self.headers)
        r_leistung = reqget(url=DualisImporter.__url, headers=self.headers, params=l_arg_dict)
        #r_leistung = req(url=leistung_url_2, headers=self.headers)

        # write not parsed into file
        #with open("response.html", "w") as f:
        #    f.write(r_leistung.text)

        # parse html content to work on it (2)
        # return BeautifulSoup(r_leistung.text, "lxml")
        #print(f"HTML BEAUTIFUL\n{ leistungen }", sys.stdout)
        # print(leistungen.prettify())
        return r_leistung.text

    def parse_HTML(self, html_data):
        print("HTML-Parser")

        table_MN = pd.read_html(html_data)

        df = table_MN[0]
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
                "total_gpa_grade": table_MN[1].columns.values.tolist()[- 1][0],
                "major_subject_gpa_grade": table_MN[1].columns.values.tolist()[- 1][1]
            }


        print(grades)

    def logout(self, args):
        """
        """
        # change PRGNAME to LOGOUT
        print("Logout")
        args["PRGNAME"] = "LOGOUT"
        r = reqget(url=DualisImporter.__url, headers=self.headers, params=args)
        # TODO DEBUG --> LOGGER
        print(f"{ r.status_code }\n{ r.headers }", sys.stdout)
