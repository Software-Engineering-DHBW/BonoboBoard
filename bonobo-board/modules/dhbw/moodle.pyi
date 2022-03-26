from typing import Any, ClassVar, Coroutine
from bs4.element import Tag

from .util import ImporterSession, MoodleCourseDict, MoodleModuleDict

#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

def add_to_module_dict(name: str, url: str) -> MoodleModuleDict: ...


def get_bbb_instance_name(tag_a: Tag) -> str: ...

#------------------------------------------------------------------------------#
# M O O D L E - I M P O R T E R
#------------------------------------------------------------------------------#

class MoodleImporter(ImporterSession):
    url: ClassVar[str]
    logout_url: str

    def __init__(self) -> None: ...

    async def login(self, username: str, password: str) -> Coroutine[Any, Any, Any]: ...

    def find_all_bbb_rooms(self, course_dict: MoodleCourseDict) -> MoodleCourseDict: ...

    async def scrape(self) -> Coroutine[Any, Any, Any]: ...

    def logout(self) -> None: ...
