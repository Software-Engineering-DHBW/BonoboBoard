# -*- coding: utf-8 -*-

from os import environ
import unittest
from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# Google Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
# Firefox
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

def check_env_vars_set():
    """check that credentials are set, otherwise fail this test"""
    if not environ.get("STUDENTMAIL") or not environ.get("STUDENTPASS") or not environ.get("STUDENTCOURSE"):
        raise Exception(
            f"To run this unittest, you must set the following variables inside your environment:"
            f"STUDENTMAIL, STUDENTPASS, STUDENTCOURSE"
        )

class TestLoginPageUI(TestCase):
    def setUp(self):
        self.browsers = [
            webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install())),
            webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        ]
        self.url = "http://localhost:80/"
        print("successful setUp")

    def tearDown(self):
        for browser in self.browsers:
            browser.close()
        print("successful tearDown")

    def test_authentication(self):
        print("start authentication testing ...")
        check_env_vars_set()
        for browser in self.browsers:
            # connect to website
            print(browser, self.url)
            browser.get(self.url)
            self.assertEqual("BonoboBoard - Login", browser.title)
            # locate inputs and fill them
            input_name = browser.find_element(by=By.NAME, value="username")
            input_name.send_keys(environ.get("STUDENTMAIL"))
            input_pass = browser.find_element(by=By.NAME, value="password")
            input_pass.send_keys(environ.get("STUDENTPASS"))
            input_course = browser.find_element(by=By.NAME, value="course")
            input_course.send_keys(environ.get("STUDENTCOURSE"))
            # get cookie (only one should be there)
            cookie = browser.get_cookies()[0]
            browser.add_cookie({"name": cookie["name"], "value": cookie["value"]})
            # locate login btn and click it
            btn_login = browser.find_element(by=By.ID, value="login")
            btn_login.click()
            print("\n\nSUCCESSFUL LOGIN!!!\n\n")

if __name__ == "__main__":
    unittest.main(verbosity=2)
