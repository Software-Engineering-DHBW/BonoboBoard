# -*- coding: utf-8 -*-

"""unittests for the dualis module
"""

from os import environ
from unittest import TestCase, TestSuite
from dhbw.dualis import DualisImporter

d_imp = DualisImporter()

class TestDualisImporter(TestCase):
    """Unittests for the dualis class.
    """
    def test_login(self):
        """Test dualis login functionality.
        """
        usr_name = environ.get("STUDENTMAIL")
        passwd = environ.get("STUDENTPASS")
        d_imp.login(usr_name, passwd)
        self.assertIsNotNone(d_imp.auth_token)
        self.assertIsNotNone(d_imp.headers["Cookie"])

    def test_scrape(self):
        """Test scraping functionality.
        """
        d_imp.scrape()
        self.assertIsNotNone(d_imp.scraped_data)

    def test_logout(self):
        """Test logout functionality.
        """
        d_imp.logout()
        self.assertEqual("", d_imp.auth_token)

    @classmethod
    def cls_suite(cls):
        """Create suite for ordered execution of unittests.
        """
        cls_suite = TestSuite()
        cls_suite.addTest(cls("test_login"))
        cls_suite.addTest(cls("test_scrape"))
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
