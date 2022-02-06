from typing import ClassVar
from util import Importer

class CourseImporter(Importer):
    __url: ClassVar[str]

class LectureImporter(Importer):
    __url: ClassVar[str]