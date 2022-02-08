from typing import ClassVar
from util import Importer
import pandas as pd

class CourseImporter(Importer):
    __url: ClassVar[str]

    def __init__(self) -> None: ...

    def scrape(self) -> None: ...


class LectureImporter(Importer):
    __url: ClassVar[str]

    def __init__(self, uid: int|str) -> None: ...

    def scrape(self, uid: int|str) -> pd.DataFrame: ...

    def limit_days_in_list(self, days_past: int, days_future: int) -> pd.DataFrame: ...

