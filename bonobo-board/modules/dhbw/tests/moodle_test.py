# -*- coding: utf-8 -*-

"""Unittests for the moodle module.
"""
import asyncio
from os import environ
from unittest import TestCase, TestSuite
from dhbw.moodle import MoodleImporter

m_imp = MoodleImporter()

class TestMoodleImporter(TestCase):
    """Unittests for the moodle class.
    """
    def test_login(self):
        """Test login functionality.
        """
        usr_name = environ.get("STUDENTMAIL")
        passwd = environ.get("STUDENTPASS")
        asyncio.run(m_imp.login(usr_name, passwd))
        self.assertIsNotNone(m_imp.auth_token)
        self.assertIsNotNone(m_imp.headers["Cookie"])

    def test_scrape(self):
        """Test scraping functionality.
        """
        asyncio.run(m_imp.scrape())
        self.assertIsNotNone(m_imp.scraped_data["courses"])

    def test_logout(self):
        """Test logout functionality.
        """
        m_imp.logout()
        self.assertEqual("", m_imp.auth_token)

    @classmethod
    def cls_suite(cls):
        """Create suite for ordered execution of unittests.
        """
        cls_suite = TestSuite()
        cls_suite.addTest(cls("test_login"))
        cls_suite.addTest(cls("test_scrape"))
        cls_suite.addTest(cls("test_logout"))
        return cls_suite
