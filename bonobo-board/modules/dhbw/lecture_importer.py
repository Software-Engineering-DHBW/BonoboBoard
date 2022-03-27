# -*- coding: utf-8 -*-

"""Provide functionality to interact with the students timetable.
"""
import asyncio
import os
from datetime import datetime, timedelta
import pandas as pd
import sqlalchemy
from bs4 import BeautifulSoup
import icalendar
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

    def limit_weeks_in_list(self, offset):
        """method to limit/crop the lectures-DataFrame gathered in LectureImporter.scrape() by limiting the weeks

        Parameters
        ----------
        offset : int
            offsets returned data by a number of weeks

        Returns
        -------
        pd.Dataframe
            cropped lectures-DataFrame
        """
        w_start = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=offset)
        w_end = w_start + timedelta(weeks=1)
        df = self.lectures
        return df[(df["start"] > w_start.replace(hour=0, minute=0, second=0)) & (
                df["start"] < w_end.replace(hour=0, minute=0, second=0))]


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
    """ Scraping lectures of all courses. Warning: Does only work in docker-container.

    Returns
    -------
    None
    """

    # Change to bonobo-working directory in docker-container
    os.chdir("/bonobo-board/")
    courses = CourseImporter()
    for course in courses.uid_list:
        print(course)
        lecture_imp = LectureImporter()
        asyncio.run(lecture_imp.scrape(course))
        df = lecture_imp.lectures
        write_lectures_to_database(df, course)


def write_lectures_to_database(lectures_df, course_uid):
    """ Write the lectures of one course to the database.

    Parameters
    ----------
    path_to_db : str

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

def _write_lecture_links_to_database(df, user_uid):  # df-columns: lecture, link
    """ Write lecture-link DataFrame to database.

    Parameters
    ----------
    df : pd.DataFrame(columns=["lecture", "link"])
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
        Creates table, for new users.
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
    try:
        result =pd.read_sql("SELECT * FROM \'" + table_name + "\';", engine)      
    except Exception:
        new_df = pd.DataFrame(columns=["lecture", "link"])
        _write_lecture_links_to_database(df=new_df, user_uid=user_uid)
        result = new_df
    return result


def add_lecture_links_to_database(user_uid, event, link):
    """ Checks, if event is already saved in database.
        Adds/Updates event in database.
    Parameters
    ----------
    user_uid : str
        user email
    event : str
        name of the event
    link : str
        link to safe to the event
    Returns
    -------
    pd.DataFrame
    """
    df = read_lecture_links_from_database(user_uid)
    if (df['lecture'] == event).any():
        #df['link'][(df['lecture'] == event).any().index] = link
        df.loc[df["lecture"] == event, "link"] = link
    else: 
        df_to_append = pd.DataFrame({"lecture": [event], "link":[link]})
        df = df.append(df_to_append)

    _write_lecture_links_to_database(df, user_uid)
