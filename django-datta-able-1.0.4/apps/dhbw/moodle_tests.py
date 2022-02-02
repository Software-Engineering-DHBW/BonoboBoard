# -*- coding: utf-8 -*-

"""unittests for the moodle module
"""

from os import environ
import unittest
from unittest import runner
import base
import moodle

USERNAME = environ.get("STUDENTMAIL")
PASSWORD = environ.get("STUDENTPASS")

class TestMoodleImporter(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        self.m_imp = moodle.MoodleImporter()

    def test_login(self):
        """"""
        self.m_imp.login(USERNAME, PASSWORD)
        self.assertIsNotNone(self.m_imp.auth_token)

    def test_scrape(self):
        """"""
        self.m_imp.scrape()
        self.assertIsInstance(self.m_imp.scraped_data, base.MoodleDict)

    def test_logout(self):
        """"""
        self.m_imp.logout()
        self.assertIsNone(self.m_imp.logout())

def suite():
    cst_suite = unittest.TestSuite()
    cst_suite.addTest(TestMoodleImporter("setUp"))
    cst_suite.addTest(TestMoodleImporter("test_login"))
    cst_suite.addTest(TestMoodleImporter("test_scrape"))
    cst_suite.addTest(TestMoodleImporter("test_logout"))
    return cst_suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
