# -*- coding: utf-8 -*-

"""unittests for the lecture module
"""
import asyncio
from unittest import TestCase

import pandas as pd

from dhbw.lecture_importer import LectureImporter
from dhbw.lecture_importer import CourseImporter

class LectureImporterTest(TestCase):
    """Unittests for the lecture class.
    """
    def test_false_uid(self):
        """Test for check of gathering lectures with wrong uid.
        """
        lec = LectureImporter()
        asyncio.run(lec.scrape(776101))
        self.assertEqual(isinstance(lec.lectures, pd.DataFrame), True)

    def test_true_uid(self):
        """Test for check of gathering lectures with right uid.
        """
        lec = LectureImporter()
        asyncio.run(lec.scrape(7761001))
        self.assertEqual(lec.lectures.empty, False)

    def test_limit_weeks_in_list(self):
        """Test for limiting weeks in lecture-list.
        """
        lec = LectureImporter()
        asyncio.run(lec.scrape(7761001))
        lec.lectures = lec.limit_weeks_in_list(3)
        self.assertEqual(isinstance(lec.lectures, pd.DataFrame), True)


class CourseImporterTest(TestCase):
    """unittests for the course module.
    """
    def test_course_importer(self):
        """Test for return of CourseImporter, length of list should be >0
        """
        courses = CourseImporter()
        self.assertFalse(len(courses.course_list) == 0)

    def test_check_values(self):
        """Test if the course list contains a specific course uid
        """
        courses = CourseImporter()
        self.assertTrue("7761001" in courses.uid_list)
