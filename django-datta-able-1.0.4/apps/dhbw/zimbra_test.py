# -*- coding: utf-8 -*-

"""unittests for the moodle module
"""

from os import environ
import unittest
from unittest import runner
from zimbra import ZimbraHandler

USERNAME = environ.get("STUDENTMAIL")
PASSWORD = environ.get("STUDENTPASS")

z_hdlr = ZimbraHandler()

class TestZimbraHandler(unittest.TestCase):
    """
    """
    def test_login(self):
        """"""
        z_hdlr.login(USERNAME, PASSWORD)
        self.assertIsNotNone(z_hdlr.auth_token)
        self.assertIsNotNone(z_hdlr.headers["Cookie"])

    def test_scrape(self):
        """"""
        z_hdlr.scrape()
        self.assertIsNotNone(z_hdlr.scraped_data)

    def test_logout(self):
        """"""
        z_hdlr.logout()
        self.assertEqual("", z_hdlr.auth_token)

def suite():
    cstm_suite = unittest.TestSuite()
    cstm_suite.addTest(TestZimbraHandler("test_login"))
    cstm_suite.addTest(TestZimbraHandler("test_scrape"))
    cstm_suite.addTest(TestZimbraHandler("test_logout"))
    return cstm_suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
