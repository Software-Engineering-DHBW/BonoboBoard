# -*- coding: utf-8 -*-

"""Provide functionality to interact with the students timetable.
"""

from datetime import datetime, timedelta
import calendar
import pandas as pd
import sqlalchemy
from bs4 import BeautifulSoup
import icalendar
import asyncio

from .util import Importer, reqget


class CourseImporter(Importer):
    """Class to achieve the list of all courses of the DHBW Mannheim.

    Attributes
    ----------
    url : str
        Universal given link for the dhbw-course-calendars.
    course_list : List[str]
        List containing all courses (e.g. "TINF19 IT2") after scraping
    uid_list : uid_list[str]
        List containing all course-uid's after scraping
    """

    url = "https://vorlesungsplan.dhbw-mannheim.de/ical.php"

    def __init__(self):
        super().__init__()
        self.course_list = []
        self.uid_list = []
        self.scrape()

    def scrape(self):
        """Method to scrape the list of all courses. List is stored in course_list and uid_list.

        Returns
        -------
        None
        """
        response = reqget(url=CourseImporter.url, headers=self.headers)
        result = BeautifulSoup(
            response.content, "lxml").find(id="class_select")

        # optgroup stores the list of courses
        all_optgroup = result.find_all('optgroup')
        for optgroup in all_optgroup:
            for course in optgroup:
                if course.get("value"):
                    self.course_list.append(course['label'])
                    self.uid_list.append(course['value'])

    def get_course_uid(self, course_str):
        """Get a course uid by providing a course name.

        Parameters
        ----------
        course_str : List[str]

        Returns
        -------
        str
        """
        index = self.course_list.index(course_str)
        return self.uid_list[index]


class LectureImporter(Importer):
    """Class to achieve the course-specific timetable.

    Attributes
    ----------
    url: str
        Universal given link for the dhbw-course-calendars.
    lectures: pd.DataFrame
        List containing all lectures of a specified course after scraping

    """

    # No HTTPS possible in this case?
    url = "http://vorlesungsplan.dhbw-mannheim.de/ical.php?uid="

    def __init__(self):
        super().__init__()
        self.lectures = None

    async def login(self):
        """Async login method for frontend

        Returns
        -------
        LectureImporter
        """
        return self

    async def scrape(self, uid):
        """Method to scrape the courses-icalendar and parse it to a pandas.DataFrame.

        Parameters
        ----------
        uid : str or int
            specific course-uid (get all courses from CourseImporter)

        Returns
        -------
        pandas.DataFrame
        """
        # set up url to the ical file
        ical_url = LectureImporter.url + str(uid)

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
        df = df.sort_values("start")
        self.lectures = df
        return df

    def limit_days_in_list(self, days_past, days_future):
        """Method to limit/crop the lectures-DataFrame gathered in LectureImporter.scrape() by limiting the days.

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

    def limit_weeks_in_list(self, weeks_past, weeks_future):
        """method to limit/crop the lectures-DataFrame gathered in LectureImporter.scrape() by limiting the weeks

        Parameters
        ----------
        weeks_past : int
            include the last x weeks in the list
        weeks_future : int
            include the future x weeks in the list

        Returns
        -------
        pd.Dataframe
            cropped lectures-DataFrame
        """
        w_past = datetime.today() - timedelta(days=datetime.today().weekday(), weeks=weeks_past)
        w_future = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=weeks_future + 1)
        df = self.lectures
        return df[(df["start"] > w_past.replace(hour=0, minute=0, second=0)) & (
                df["start"] < w_future.replace(hour=0, minute=0, second=0))]


# ?: remove (its cool that we can do it, but I dont see a reason for this to exist) @NK
# NK: Its cool that we can do it, but its also mandatory (load all courses for database with cronjob) @Anonymous
def all_courses_lectures(limit_days_past=14, limit_days_future=14):
    """Gather lectures for all available courses.

    Parameters
    ----------
    limit_days_past : int
        Only save lectures of the last x days.
    limit_days_future : int
        Only save lectures of the future x days.
    Returns
    -------
    list
        Containing 2 lists (all_courses (uid), all_lectures (array with all lectures for every course).
    """
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
        df = lectures.limit_days_in_list(limit_days_past, limit_days_future).copy()
        df['c_uid'] = course
        all_lectures = pd.concat([all_lectures, df], ignore_index=True)

    return [all_courses, all_lectures]


# -------------- HELPERS --------------------

def _get_unique_lectures(df_lectures):
    """Function to get unique lectures of given lecture-plan.

    Parameters
    ----------
    df_lectures : pandas.DataFrame

    Returns
    -------
    data : list
        List of unique lectures

    """
    unique = df_lectures["lecture"].unique()
    data = []
    for entry in unique:
        data.append(str(entry))
    return data


def create_empty_user_links_df(df_lectures):
    """Function to create an empty link table.

    Parameters
    ----------
    df_lectures : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    unique_lectures = _get_unique_lectures(df_lectures)
    df_links = pd.DataFrame()
    df_links["lecture"] = unique_lectures
    df_links["link"] = ""
    return df_links


def link_lectures_and_links(df_lectures, df_links):
    """Function to link lectures and link DataFrames.

    Parameters
    ----------
    df_lectures : pd.DataFrame
    df_links : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df_lectures.copy()
    df["link"] = "NO LINK"
    for unique_lecture in df_lectures["lecture"].unique():
        link_for_unique = df_links[df_links["lecture"]
                                   == unique_lecture]["link"].values[0]
        df.loc[df["lecture"] == unique_lecture, "link"] = link_for_unique
    return df


# ----------------- COURSE DATABASE --------------------
# WRITE
def write_courses_to_database():
    """ Write all courses to database.

    Returns
    -------
    None
    """
    courses = CourseImporter()
    engine_string = "sqlite:///courses.db"
    engine = sqlalchemy.create_engine(engine_string)

    df = pd.DataFrame(columns=["course", "uid"])
    for i in range(0, len(courses.course_list)):
        df.loc[i] = [courses.course_list[i], courses.uid_list[i]]
    df.to_sql("courses", engine, if_exists='replace', index=False)
    return


# READ
def read_courses_from_database():
    """ Read all courses from database.

    Returns
    -------
    List[str], List[str]
        Course and uid list.
    """
    engine_string = "sqlite:///courses.db"
    engine = sqlalchemy.create_engine(engine_string)
    df = pd.read_sql("SELECT * FROM \'courses\';", engine)
    return df['course'].tolist(), df['uid'].tolist()


# ----------------- LECTURE DATABASE --------------------
# WRITE
def write_all_courses_lectures_to_database():
    """ Scraping lectures of all courses. Warning: May take while.

    Returns
    -------
    None
    """
    courses = CourseImporter()
    print("Length Course-List:", len(courses.uid_list))
    for course in courses.uid_list:
        lectures = LectureImporter(course)
        df = lectures.limit_days_in_list(14, 14).copy()
        write_lectures_to_database(df, course)


def write_lectures_to_database(lectures_df, course_uid):
    """ Write the lectures of one course to the database.

    Parameters
    ----------
    lectures_df : pd.DataFrame
    course_uid : str

    Returns
    -------

    """
    engine_string = "sqlite:///lectures.db"
    engine = sqlalchemy.create_engine(engine_string)
    lectures_df.to_sql(str(course_uid), engine, if_exists='replace', index=False)
    return


# READ
def read_lectures_from_database(course_uid):
    """ Read lectures of specified course from database.

    Parameters
    ----------
    course_uid : str

    Returns
    -------
    pd.DataFrame
        Contains lectures.
    """
    engine_string = "sqlite:///lectures.db"
    engine = sqlalchemy.create_engine(engine_string)
    return pd.read_sql("SELECT * FROM \'" + str(course_uid) + "\';", engine)


# ----------------- LECTURE LINK DATABASE --------------------

def write_lecture_links_to_database(df, user_uid):  # df-columns: lecture, link
    """ Write lecture-link DataFrame to database.

    Parameters
    ----------
    df : pd.DataFrame(columns=["lecture", "link"]
    user_uid : str

    Returns
    -------
    None
    """

    engine_string = "sqlite:///users.db"
    table_name = str(user_uid) + "_link"
    engine = sqlalchemy.create_engine(engine_string)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    return


def read_lecture_links_from_database(user_uid):
    """ Read lecture-link DataFrame from database.

    Parameters
    ----------
    user_uid : str

    Returns
    -------
    pd.DataFrame
    """
    engine_string = "sqlite:///users.db"
    table_name = str(user_uid) + "_link"
    engine = sqlalchemy.create_engine(engine_string)
    return pd.read_sql("SELECT * FROM \'" + table_name + "\';", engine)
