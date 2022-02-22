#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provide unittests for the dhbw module"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from unittest import makeSuite, TestSuite,  TextTestRunner

from dhbw.tests.lecture_test import LectureImporterTest, CourseImporterTest
from dhbw.tests.moodle_test import TestMoodleImporter
from dhbw.tests.zimbra_test import TestZimbraHandler
from dhbw.tests.dualis_test import TestDualisImporter

parser = ArgumentParser(
    description="Run all tests or a subset of tests",
    epilog="If no option is given, then all tests will run",
    formatter_class=ArgumentDefaultsHelpFormatter,
    prog="dhbw_test"
)
parser.add_argument("-t", "--tests", action="extend",
    choices=["course", "dualis", "lecture", "moodle", "zimbra"],
    help="Choose sets of tests to run", nargs="+", type=str
)
args = parser.parse_args()

def suite():
    """Gather all tests defined in the tests module inside the dhbw module"""
    test_suite = TestSuite()
    _args = args.tests

    if not _args:
        test_suite.addTest(makeSuite(LectureImporterTest))
        test_suite.addTest(makeSuite(CourseImporterTest))
        test_suite.addTest(TestMoodleImporter.cls_suite())
        test_suite.addTest(TestZimbraHandler.cls_suite())
    else:
        i = 0
        while i < len(_args):
            if _args[i] == "course":
                test_suite.addTest(makeSuite(CourseImporterTest))
            elif _args[i] == "dualis":
                test_suite.addTest(TestDualisImporter.cls_suite())
            elif _args[i] == "lecture":
                test_suite.addTest(makeSuite(LectureImporterTest))
            elif _args[i] == "moodle":
                test_suite.addTest(TestMoodleImporter.cls_suite())
            else:
                test_suite.addTest(TestZimbraHandler.cls_suite())
            i+=1

    return test_suite

def main():
    """Run the provided tests"""
    dhbw_suite = suite()
    runner = TextTestRunner(verbosity=2)
    test_result = runner.run(dhbw_suite)
    if test_result.errors != 0 and test_result.failures != 0:
        exit(1)


main()
