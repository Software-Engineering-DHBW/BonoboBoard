# -*- coding: utf-8 -*-

"""This module runs every unittest in relation to the 'Leistungsübersicht' page
and ensures, that every functionality of this page works as excepted.
"""

import sys
from unittest import TestSuite, TextTestRunner
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from dhbw.tests.dualis_test import TestDualisImporter
from frontend_ui.pages_ui import TestPagesUI

parser = ArgumentParser(
    description="Run all tests or a subset of tests",
    epilog="If no option is given, then all tests will run",
    formatter_class=ArgumentDefaultsHelpFormatter,
    prog="dhbw_test"
)
parser.add_argument("-b", "--browser", action="extend",
                    choices=["firefox", "chrome", "brave"],
                    help="Choose browser to run the UI tests", nargs="+", type=str
                    )
args = parser.parse_args()

def suite():
    """import all tests regarding the 'Leistungsübersicht' page"""
    test_suite = TestSuite()
    browsers = list(args.browser)
    if not browsers:
        browsers = ["firefox", "chrome", "brave"]
    TestPagesUI().set_drivers(browsers)
    test_suite.addTest(TestDualisImporter.cls_suite())
    test_suite.addTest(TestPagesUI.cls_suite())
    return test_suite

# YOU CAN SAFELY IGNORE THE WARNING ABOUT RESOURCEWARNING
# see here for details: https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/5923
if __name__ == "__main__":
    runner = TextTestRunner(verbosity=2)
    test_result = runner.run(suite())
    if len(test_result.errors) != 0 or len(test_result.failures) != 0:
        sys.exit(1)
