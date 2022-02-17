from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict, List, Literal, NoReturn, TypedDict, Union
from requests.models import Response

class MoodleModuleDict(TypedDict):
    name: str
    url: str

class MoodleCourseDict(TypedDict):
    name: str
    href: str
    bbb_rooms: List[MoodleModuleDict]

MoodleDict = Dict[str, Union[List[MoodleCourseDict], str]]

class DualisModuleDict(TypedDict):
    id: str
    href: str
    name: str
    credits: int
    grade: float
    state: Literal["f", "o", "p"]

class DualisDict(TypedDict):
    gpa_total: float
    gpa_main_subject: float
    modules: List[DualisModuleDict]

def reqpost(
    *,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, str],
    payload: Dict[str, str],
    allow_redirects: bool,
    return_code: int
) -> Union[Response, NoReturn]: ...

def reqget(
    *,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, str],
    allow_redirects: bool,
    return_code: int
) -> Union[Response, NoReturn]: ...

def url_get_fqdn(url: str) -> str: ...

def url_get_path(url: str) -> str: ...

def url_get_args(url: str) -> List[str]: ...

class Importer(ABC):
    headers: Dict[str, str]
    scraped_data: Dict[str, Union[MoodleDict, DualisDict, Any]]

    def __init__(self) -> None: ...

    def drop_header(self, header: str) -> None: ...

class ImporterSession(Importer, metaclass=ABCMeta):
    auth_token: str

    def __init__(self) -> None: ...

    @abstractmethod
    def login(self, username: str, password: str) -> None: ...

    @abstractmethod
    def scrape(self) -> None: ...

    @abstractmethod
    def logout(self) -> None: ...
