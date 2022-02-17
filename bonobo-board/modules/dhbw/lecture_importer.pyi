from typing import ClassVar, List
from pandas import DataFrame

from .util import Importer

class CourseImporter(Importer):
    url: ClassVar[str]
    course_list = List[str]
    uid_list = List[str]

    def __init__(self) -> None: ...

    def scrape(self) -> None: ...

class LectureImporter(Importer):
    url: ClassVar[str]
    lectures: DataFrame

    def __init__(self, uid: int|str) -> None: ...

    def scrape(self, uid: int|str) -> DataFrame: ...

    def limit_days_in_list(self, days_past: int, days_future: int) -> DataFrame: ...

def all_course_lectures() -> List[DataFrame]: ...
