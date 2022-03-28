# -*- coding: utf-8 -*-

"""This module contains possible unittests for the frontend (UI).
"""

from os import environ, devnull
import unittest
from unittest import TestCase, TestSuite

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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

def add_browsers_to_test(drivers):
    """add browsers to the unittest"""
    browsers = []
    for elem in drivers:
        elem = str(elem)
        if elem == "chrome":
            options = webdriver.ChromeOptions()
            options.add_experimental_option("detach", True)
            options.add_argument("--start-maximized")
            browsers.append(
                webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options
                )
            )
        elif elem == "brave":
            options = webdriver.ChromeOptions()
            options.add_experimental_option("detach", True)
            options.add_argument("--start-maximized")
            browsers.append(
                webdriver.Chrome(
                    service=ChromeService(
                        ChromeDriverManager(
                            chrome_type=ChromeType.BRAVE
                        ).install()
                    ),
                    options=options
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
        """get the browser objects"""
        self.browsers = add_browsers_to_test(self.drivers)

    def test_everything(self):
        """full feature test"""
        check_env_vars_set()
        for browser in self.browsers:
            browser.get(fconf.URL)
            self.assertEqual("BonoboBoard - Login", browser.title)
            # fill login form
            fill_input_form(browser)
            # locate login btn and click it
            login_btn = browser.find_element(by=By.ID, value="login")
            login_btn.click()
            wait = WebDriverWait(browser,10)
            wait.until(EC.url_changes(fconf.URL))
            browser.implicitly_wait(3)
            icon_btn = browser.find_element(by=By.ID, value="icon")
            icon_btn.click()
            gpa_div = browser.find_element(by=By.ID, value="gpa")
            gpa_div_p = gpa_div.find_element(by=By.TAG_NAME, value="p")
            self.assertRegex(gpa_div_p.text, r"GPA-Total:\x20[0-6]\.[0-9]$")
            browser.implicitly_wait(3)
            navbar_grades = browser.find_element(by=By.LINK_TEXT, value="Leistungsübersicht")
            navbar_grades.click()
            self.assertIn("/leistungsuebersicht", browser.current_url)
            all_grades_div = browser.find_element(by=By.ID, value="all_grades")
            tbody = all_grades_div.find_element(by=By.TAG_NAME, value="tbody")
            grades = tbody.text.split("\n")
            self.assertRegex(grades[0], r".+\x20[0-9]+\x20[0-6]\.[0-9]$")

    def tearDown(self):
        """quit all used browsers"""
        for browser in self.browsers:
            browser.quit()

    @classmethod
    def cls_suite(cls):
        """make a suite for this test"""
        cls_suite = TestSuite()
        cls_suite.addTest(cls("test_everything"))
        return cls_suite

    @classmethod
    def set_drivers(cls, driver_list):
        """set drivers for the test"""
        cls.drivers = driver_list.copy()

# YOU CAN SAFELY IGNORE THE WARNING ABOUT RESOURCEWARNING
# see here for details: https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/5923
if __name__ == "__main__":
    TestPagesUI().set_drivers(["firefox", "chrome", "brave"])
    unittest.main(verbosity=2)
