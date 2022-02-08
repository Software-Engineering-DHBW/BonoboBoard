import unittest

import lecture_test


def suite():
    """ Gather all tests from this module in a test suite.

    """
    print("\n-------------------- Adding Tests --------------------\n")
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(lecture_test.LectureImporterTest))
    test_suite.addTest(unittest.makeSuite(lecture_test.CourseImporterTest))
    return test_suite


print("------------------------------------------------------")
print("----------------- Starting TestSuite -----------------")
print("------------------------------------------------------")

mySuite = suite()
runner = unittest.TextTestRunner(verbosity=2)
runner.run(mySuite)
