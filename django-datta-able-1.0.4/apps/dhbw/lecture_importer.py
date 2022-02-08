from datetime import datetime, timedelta

import icalendar
import pandas as pd
from bs4 import BeautifulSoup

from util import *


class CourseImporter(Importer):
    """class to achieve the list of all courses of the DHBW Mannheim

    """

    __url = "https://vorlesungsplan.dhbw-mannheim.de/ical.php"

    # TODO @JH delete auth token ?
    def __init__(self) -> None:
        super().__init__()
        self.course_list = []
        self.uid_list = []
        self.scrape()

    def scrape(self) -> None:
        """method to scrape the list of all courses

        list is stored in course_list

        Returns
        -------
        None
        """
        response = reqget(url=CourseImporter.__url, headers=self.headers)
        result = BeautifulSoup(response.content, "html.parser").find(id="class_select")

        # optgroup stores the list of courses
        all_optgroup = result.find_all('optgroup')
        for optgroup in all_optgroup:
            for course in optgroup:
                if course.get("value"):
                    self.course_list.append(course['label'])
                    self.uid_list.append(course['value'])


class LectureImporter(Importer):
    """class to achieve the course-specific timetable

    """

    # No HTTPS possible in this case?
    __url = "http://vorlesungsplan.dhbw-mannheim.de/ical.php?uid="

    # TODO @JH delete auth token ?
    def __init__(self, uid) -> None:
        super().__init__()
        self.lectures = self.scrape(uid)

    def scrape(self, uid) -> pd.DataFrame:
        """method to scrape the courses-icalendar and parse it to a pandas.DataFrame

        Parameters
        ----------
        uid : str or int
            specific course-uid (get all courses from CourseImporter)

        Returns
        -------
        pandas.DataFrame
        """
        # set up url to the ical file
        ical_url = LectureImporter.__url + str(uid)

        # Get ical from given address
        response = reqget(url=ical_url, headers=self.headers,
                          allow_redirects=True)
        gcal = icalendar.Calendar.from_ical(response.content)

        df = pd.DataFrame(columns=["lecture", "location", "start", "end"])
        for component in gcal.walk():
            if component.name == "VEVENT":
                vevent = [component.get('SUMMARY'),
                          component.get('LOCATION'),
                          component.get('DTSTART').dt,
                          component.get('DTEND').dt
                          ]
                df.loc[len(df)] = vevent
        return df

    def limit_days_in_list(self, days_past, days_future) -> pd.DataFrame:
        """method to limit/crop the lectures-DataFrame gathered in LectureImporter.scrape() by limiting the days

        Parameters
        ----------
        days_past : int
            include the last x days in the list
        days_future : int
            include the future x days in the list

        Returns
        -------
        pandas.Dataframe
            cropped lectures-DataFrame
        """
        d_past = datetime.today() - timedelta(days=days_past)
        d_future = datetime.today() + timedelta(days=days_future)
        df = self.lectures
        return df[(df["start"] > d_past) & (df["start"] < d_future)]


def all_courses_lectures():
    courses = CourseImporter()
    all_lectures = pd.DataFrame(columns=["lecture", "location", "start", "end", "c_uid"])  # foreign key c_uid
    print(len(courses.uid_list))
    course_data = list(zip(courses.uid_list, courses.course_list))
    all_courses = pd.DataFrame(course_data, columns=["c_uid", "name"])
    i = 0
    for course in courses.uid_list:
        i += 1
        if i > 0 and i % 10 == 0:
            print(i)
        lectures = LectureImporter(course)
        df = lectures.limit_days_in_list(14, 14).copy()
        df['c_uid'] = course
        all_lectures = pd.concat([all_lectures, df], ignore_index=True)

    return [all_courses, all_lectures]


if __name__ == '__main__':
    print("main lecture_importer.py")
    # all_courses_lectures()
