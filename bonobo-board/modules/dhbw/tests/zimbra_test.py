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
        cls_suite.addTest(cls("test_send_mail"))
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
