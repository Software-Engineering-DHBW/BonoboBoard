# -*- coding: utf-8 -*-

"""unittests for the moodle module
"""

from os import environ
from unittest import TestCase, TestSuite
from dhbw.moodle import MoodleImporter

m_imp = MoodleImporter()

class TestMoodleImporter(TestCase):
    """unittests for the moodle class
    """
    def test_login(self):
        """test login functionality
        """
        usr_name = environ.get("STUDENTMAIL")
        passwd = environ.get("STUDENTPASS")
        m_imp.login(usr_name, passwd)
        self.assertIsNotNone(m_imp.auth_token)
        self.assertIsNotNone(m_imp.headers["Cookie"])

    def test_scrape(self):
        """test scraping functionality
        """
        m_imp.scrape()
        self.assertIsNotNone(m_imp.scraped_data["courses"])

    def test_logout(self):
        """test logout functionality
        """
        m_imp.logout()
        self.assertEqual("", m_imp.auth_token)

    @classmethod
    def cls_suite(cls):
        """create suite for ordered execution of unittests
        """
        cls_suite = TestSuite()
        cls_suite.addTest(cls("test_login"))
        cls_suite.addTest(cls("test_scrape"))
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
