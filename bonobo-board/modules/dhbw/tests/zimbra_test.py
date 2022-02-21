# -*- coding: utf-8 -*-

"""unittests for the zimbra module
"""

from os import environ
from unittest import TestCase, TestSuite
from dhbw.zimbra import ZimbraHandler

z_hdlr = ZimbraHandler()

class TestZimbraHandler(TestCase):
    """unittests for the zimbra class"""
    def test_login(self):
        """test login functionality"""
        usr_name = environ.get("STUDENTMAIL")
        passwd = environ.get("STUDENTPASS")
        z_hdlr.login(usr_name, passwd)
        self.assertIsNotNone(z_hdlr.auth_token)
        self.assertIsNotNone(z_hdlr.headers["Cookie"])
        self.assertIsNotNone(z_hdlr.accountname)

    def test_scrape(self):
        """test scraping functionality"""
        z_hdlr.scrape()
        self.assertIsNotNone(z_hdlr.scraped_data)
        self.assertIsNotNone(z_hdlr.realname)

    def test_get_contacts(self):
        """test get contacts functionality"""
        z_hdlr.get_contacts()
        self.assertIsNotNone(z_hdlr.contacts)

    def test_new_contact(self):
        """test creating a new contact"""
        contact = {
            "email": "unittest@bonoboboard.de",
            "firstName": "unittest",
            "lastName": "bonoboboard",
            "jobTitle": "BONOBOTESTER"
        }
        z_hdlr.new_contact(contact)

        contact_found = False
        for elem in z_hdlr.contacts:
            if elem["firstName"] == contact["firstName"]:
                contact_found = True
        # meaningful test output
        print(f"\n\n>>> Created Contact: \"{ contact_found }\"\n")

        self.assertIn(contact, z_hdlr.contacts)

    def test_remove_contact(self):
        """test removing an existing contact"""
        contact_id = ""
        for elem in z_hdlr.contacts:
            if elem["firstName"] == "unittest":
                contact_id = elem["id"]
                break

        # meaningful test output
        print(f"\n\n>>> Removing contact with firstName \"unittest\" and id \"{ contact_id }\"")

        z_hdlr.remove_contact(contact_id)
        contact_found = False
        for elem in z_hdlr.contacts:
            if not elem:
                continue
            if elem["firstName"] == "unittest":
                contact_found = True
                break

        # meaningful test output
        print(f">>> Contact found locally: \"{ contact_found }\"\n")

        self.assertFalse(contact_found)

    def test_send_mail(self):
        """test send mail functionality"""
        mymail = environ.get("STUDENTMAIL")
        mail_dict = {
            "recipients": [mymail],
            "rec_cc": [],
            "rec_bcc": [],
            "subject": "Unittest Zimbra",
            "cttype": "text/plain",
            "content": "Hello there my old me,\n\nif this mail reached you then sending mails works as expected\n\nBest Regards\n~ future you ~"
        }
        z_hdlr.send_mail(mail_dict)

    def test_logout(self):
        """test logout functionality"""
        z_hdlr.logout()
        self.assertEqual("", z_hdlr.auth_token)

    @classmethod
    def cls_suite(cls):
        """create suite for ordered execution of unittests"""
        cls_suite = TestSuite()
        cls_suite.addTest(cls("test_login"))
        cls_suite.addTest(cls("test_scrape"))
        cls_suite.addTest(cls("test_get_contacts"))
        cls_suite.addTest(cls("test_new_contact"))
        cls_suite.addTest(cls("test_remove_contact"))
        cls_suite.addTest(cls("test_send_mail"))
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
