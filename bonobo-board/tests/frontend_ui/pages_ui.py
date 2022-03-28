# -*- coding: utf-8 -*-

"""This module contains possible unittests for the frontend (UI).
"""

from os import environ, devnull
import unittest
from unittest import TestCase

from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

# global settings for this project
import frontend_config as fconf

def check_env_vars_set():
    """check that credentials are set, otherwise fail this test"""
    mail = environ.get("STUDENTMAIL")
    password = environ.get("STUDENTPASS")
    course = environ.get("STUDENTCOURSE")
    if not mail or not password or not course:
        raise Exception(
            "To run this unittest, you must set the following variables inside your environment: "
            "STUDENTMAIL, STUDENTPASS, STUDENTCOURSE"
        )

def fill_input_form(driver):
    """locate the input fields of the login form and fill them with values"""
    # locate inputs and fill them
    driver.find_element(by=By.NAME, value="username").send_keys(environ.get("STUDENTMAIL"))
    driver.find_element(by=By.NAME, value="password").send_keys(environ.get("STUDENTPASS"))
    driver.find_element(by=By.NAME, value="course").send_keys(environ.get("STUDENTCOURSE"))
    # get cookie (only one should be there)
    cookie = driver.get_cookies()[0]
    driver.add_cookie({"name": cookie["name"], "value": cookie["value"]})

def add_browsers_to_test():
    """add browsers to the unittest"""
    browsers = []
    for elem in drivers:
        if elem == "chrome":
            options = webdriver.ChromeOptions()
            browsers.append(
                webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options.add_experimental_option("detach", True)
                )
            )
        elif elem == "brave":
            options = webdriver.ChromeOptions()
            browsers.append(
                webdriver.Chrome(
                    service=ChromeService(
                        ChromeDriverManager(
                            chrome_type=ChromeType.BRAVE
                        ).install()
                    ),
                    options=options.add_experimental_option("detach", True)
                )
            )
        elif elem == "firefox":
            browsers.append(
                webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    service_log_path=devnull
                )
            )
        else:
            raise Exception("Unsupported Browser!!!")
    return browsers

def url_changed(browser, url):
    """wait until redirect from login page"""
    return browser.current_url != url

class TestPagesUI(TestCase):
    """Test Class for the frontend UI"""
    def setUp(self):
        """set up for browser tests"""
        self.browsers = add_browsers_to_test()

    def test_everything(self):
        """full feature test"""
        check_env_vars_set()
        for browser in self.browsers:
            browser.get(fconf.URL)
            login_url = browser.current_url
            self.assertEqual("BonoboBoard - Login", browser.title)
            # fill login form
            fill_input_form(browser)
            # locate login btn and click it
            browser.find_element(by=By.ID, value="login").click()
            wait = WebDriverWait(browser, 10)
            wait.until(lambda browser: browser.current_url != login_url)
            browser.find_element(by=By.ID, value="icon").click()
            gpa_div = browser.find_element(by=By.ID, value="gpa")
            gpa_div_p = gpa_div.find_element(by=By.TAG_NAME, value="p")
            self.assertRegex(gpa_div_p.text, r"GPA-Total:\x20[0-6]\.[0-9]$")
            browser.find_element(by=By.LINK_TEXT, value="Leistungsübersicht").click()
            self.assertIn("/leistungsuebersicht", browser.current_url)
            all_grades_div = browser.find_element(by=By.ID, value="all_grades")
            tbody = all_grades_div.find_element(by=By.TAG_NAME, value="tbody")
            grades = tbody.text.split("\n")
            self.assertRegex(grades[0], r".+\x20[0-9]+\x20[0-6]\.[0-9]$")

    # def test_authentication(self):
    #     """test UI authentication for the browser"""
    #     check_env_vars_set()
    #     for browser in self.browsers:
    #         browser.get(fconf.URL)
    #         self.assertEqual("BonoboBoard - Login", browser.title)
    #         # fill login form
    #         fill_input_form(browser)
    #         # locate login btn and click it
    #         browser.find_element(by=By.ID, value="login").click()


    # def test_leistungsuebersicht_home(self):
    #     """assert that the gpa total grade is set on the homepage"""
    #     for browser in self.browsers:
    #         browser.get(fconf.URL)
    #         gpa_div = browser.find_element(by=By.ID, value="gpa")
    #         gpa_div_p = gpa_div.find_element(by=By.TAG_NAME, value="p")
    #         self.assertRegex(gpa_div_p.text, r"GPA-Total:\x20[1-6]\.[0-9]")

    def tearDown(self):
        """quit all used browsers"""
        for browser in self.browsers:
            browser.quit()

# YOU CAN SAFELY IGNORE THE WARNING ABOUT RESOURCEWARNING
# see here for details: https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/5923
if __name__ == "__main__":
    global drivers
    drivers = ["firefox", ]
    unittest.main(verbosity=2)