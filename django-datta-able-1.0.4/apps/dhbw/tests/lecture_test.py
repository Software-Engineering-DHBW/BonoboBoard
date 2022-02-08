import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lecture_importer import LectureImporter
from lecture_importer import CourseImporter


class LectureImporterTest(unittest.TestCase):

    def test_false_uid(self):
        lec = LectureImporter(776101)
        self.assertEqual(lec.lectures.empty, True)  # add assertion here

    def test_true_uid(self):
        lec = LectureImporter(7761001)
        self.assertEqual(lec.lectures.empty, False)  # add assertion here

    def test_limit_days_in_list(self):
        lec = LectureImporter(7761001)
        lec.lectures = lec.limit_days_in_list(7, 7)
        self.assertEqual(lec.lectures.empty, False)


class CourseImporterTest(unittest.TestCase):
    def test_course_importer(self):
        courses = CourseImporter()
        self.assertFalse(len(courses.course_list) == 0)

    def test_check_values(self):
        courses = CourseImporter()
        self.assertTrue("7761001" in courses.uid_list)


if __name__ == '__main__':
    unittest.main()
