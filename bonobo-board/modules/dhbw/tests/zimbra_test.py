# -*- coding: utf-8 -*-

"""Unittests for the zimbra module.
"""
import asyncio
from os import environ
from unittest import TestCase, TestSuite
from dhbw.zimbra import ZimbraHandler

zimbra_handler = ZimbraHandler()

class TestZimbraHandler(TestCase):
    """Unittests for the zimbra class.
    """
    def test_login(self):
        """Test login functionality.
        """
        usr_name = environ.get("STUDENTMAIL")
        passwd = environ.get("STUDENTPASS")
        asyncio.run(zimbra_handler.login(usr_name, passwd))
        self.assertIsNotNone(zimbra_handler.auth_token)
        self.assertIsNotNone(zimbra_handler.headers["Cookie"])
        self.assertIsNotNone(zimbra_handler.accountname)

    def test_scrape(self):
        """Test scraping functionality.
        """
        asyncio.run(zimbra_handler.scrape())
        self.assertIsNotNone(zimbra_handler.scraped_data)
        self.assertIsNotNone(zimbra_handler.realname)

    def test_get_contacts(self):
        """Test get contacts functionality.
        """
        zimbra_handler.get_contacts()
        self.assertIsNotNone(zimbra_handler.contacts)

    def test_new_contact(self):
        """Test creating a new contact.
        """
        contact = {
            "email": "unittest@bonoboboard.de",
            "firstName": "unittest",
            "lastName": "bonoboboard",
            "jobTitle": "BONOBOTESTER"
        }
        zimbra_handler.new_contact(contact)

        contact_found = False
        for elem in zimbra_handler.contacts:
            if elem["firstName"] == contact["firstName"]:
                contact_found = True
        # meaningful test output
        print(f"\n\n>>> Created Contact: \"{ contact_found }\"\n")

        self.assertIn(contact, zimbra_handler.contacts)

    def test_remove_contact(self):
        """Test removing an existing contact (created by test_new_contact).
        """
        contact_id = ""
        for elem in zimbra_handler.contacts:
            if elem["firstName"] == "unittest":
                contact_id = elem["id"]
                break

        # meaningful test output
        print(f"\n\n>>> Removing contact with firstName \"unittest\" and id \"{ contact_id }\"")

        zimbra_handler.remove_contact(contact_id)
        contact_found = False
        for elem in zimbra_handler.contacts:
            if not elem:
                continue
            if elem["firstName"] == "unittest":
                contact_found = True
                break

        # meaningful test output
        print(f">>> Contact found locally: \"{ contact_found }\"\n")

        self.assertFalse(contact_found)

    def test_send_mail(self):
        """Test send mail functionality by sending a mail.
        """
        mymail = environ.get("STUDENTMAIL")
        mail_dict = {
            "recipients": [mymail],
            "rec_cc": [],
            "rec_bcc": [],
            "subject": "Unittest Zimbra",
            "cttype": "text/plain",
            "content": "Hello there my old me,\n\nif this mail reached you then sending mails works as expected\n\nBest Regards\n~ future you ~"
        }
        zimbra_handler.send_mail(mail_dict)

    def test_logout(self):
        """Test logout functionality.
        """
        zimbra_handler.logout()
        self.assertEqual("", zimbra_handler.auth_token)

    @classmethod
    def cls_suite(cls):
        """Create suite for ordered execution of unittests.
        """
        cls_suite = TestSuite()
        cls_suite.addTest(cls("test_login"))
        cls_suite.addTest(cls("test_scrape"))
        cls_suite.addTest(cls("test_get_contacts"))
        cls_suite.addTest(cls("test_new_contact"))
        cls_suite.addTest(cls("test_remove_contact"))
        cls_suite.addTest(cls("test_send_mail"))
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
