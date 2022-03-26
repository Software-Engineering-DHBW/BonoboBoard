from abc import ABC, ABCMeta, abstractmethod
from typing import (
    Any, Coroutine, Dict, List,
    Literal, NoReturn, TypedDict, Union
)
from requests.models import Response

#------------------------------------------------------------------------------#
# C U S T O M - E R R O R - C L A S S E S
#------------------------------------------------------------------------------#

class ReturnCodeException(Exception):
    actual_return_code: int
    msg: str
    status_code: int

    def __init__(
        self, status_code: int,
        actual_return_code: int, msg: str) -> None: ...

    def __str__(self) -> str: ...


class ServiceUnavailableException(Exception):
    msg: str

    def __init__(self, msg: str) -> None: ...

    def __str__(self) -> str: ...


class CredentialsException(Exception):
    msg: str

    def __init__(self, msg: str) -> None: ...

    def __str__(self) -> str: ...


class LoginRequiredException(Exception):
    msg: str

    def __init__(self, msg: str) -> None: ...

    def __str__(self) -> str: ...


#------------------------------------------------------------------------------#
# T Y P E D - D A T A - S T R U C T U R E S
#------------------------------------------------------------------------------#

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


#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

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


#------------------------------------------------------------------------------#
# B A S E - C L A S S E S
#------------------------------------------------------------------------------#

class Importer(ABC):
    headers: Dict[str, str]
    scraped_data: Dict[str, Union[MoodleDict, DualisDict, Any]]

    def __init__(self) -> None: ...

    def drop_header(self, header: str) -> None: ...


class ImporterSession(Importer, metaclass=ABCMeta):
    auth_token: str
    email: str

    def __init__(self) -> None: ...

    @abstractmethod
    async def login(self, username: str, password: str) -> Coroutine[Any, Any, Any]: ...

    @abstractmethod
    async def scrape(self) -> Coroutine[Any, Any, Any]: ...

    @abstractmethod
    def logout(self) -> None: ...
