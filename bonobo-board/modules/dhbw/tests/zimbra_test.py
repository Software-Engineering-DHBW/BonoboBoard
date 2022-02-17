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

    def test_scrape(self):
        """test scraping functionality"""
        z_hdlr.scrape()
        self.assertIsNotNone(z_hdlr.scraped_data)

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
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
