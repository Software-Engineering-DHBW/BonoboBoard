# -*- coding: utf-8 -*-

"""unittests for the dualis module
"""

from os import environ
import unittest
from unittest import runner
from dualis import DualisImporter

USERNAME = environ.get("STUDENTMAIL")
PASSWORD = environ.get("STUDENTPASS")

d_imp = DualisImporter()


class TestDualisImporter(unittest.TestCase):
    """
    """

    def test_login(self):
        """
        """
        d_imp.login(USERNAME, PASSWORD)
        self.assertIsNotNone(d_imp.auth_token)
        self.assertIsNotNone(d_imp.headers["Cookie"])

    def test_scrape(self):
        """
        """
        d_imp.scrape()
        # print(d_imp.scraped_data)
        self.assertIsNotNone(d_imp.scraped_data)

    def test_logout(self):
        """
        """
        d_imp.logout()
        self.assertEqual("", d_imp.auth_token)


def suite():
    cst_suite = unittest.TestSuite()
    cst_suite.addTest(TestDualisImporter("test_login"))
    cst_suite.addTest(TestDualisImporter("test_scrape"))
    cst_suite.addTest(TestDualisImporter("test_logout"))
    return cst_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())