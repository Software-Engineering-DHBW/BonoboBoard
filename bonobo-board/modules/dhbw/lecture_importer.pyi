from typing import ClassVar, List
from pandas import DataFrame

from .util import Importer


class CourseImporter(Importer):
    url: ClassVar[str]
    course_list = List[str]
    uid_list = List[str]

    def __init__(self) -> None: ...

    def scrape(self) -> None: ...

    def get_course_uid(self, course_name: str) -> str: ...


class LectureImporter(Importer):
    url: ClassVar[str]
    lectures: DataFrame

    def __init__(self, uid: int | str) -> None: ...

    def scrape(self, uid: int | str) -> DataFrame: ...

    def limit_days_in_list(self, days_past: int, days_future: int) -> DataFrame: ...


def all_courses_lectures(limit_days_past: int, limit_days_future: int) -> List[DataFrame, DataFrame]: ...


def _get_unique_lectures(df_lectures: DataFrame) -> List[str]: ...


def create_empty_user_links_df(df_lectures: DataFrame) -> DataFrame: ...


def link_lectures_and_links(df_lectures: DataFrame, df_links: DataFrame) -> DataFrame: ...


def write_courses_to_database() -> None: ...


def read_courses_from_database() -> (List[str], List[str]): ...


def write_all_courses_lectures_to_database() -> None: ...


def write_lectures_to_database(lectures_df: DataFrame, course_uid: DataFrame) -> None: ...


def read_lectures_from_database(course_uid: str) -> DataFrame: ...


def write_lecture_links_to_database(df: DataFrame, user_uid: str) -> None: ...


def read_lecture_links_from_database(user_uid: str) -> DataFrame: ...
