from typing import Any, ClassVar, Coroutine, Dict, Literal

from .util import DualisModuleDict, ImporterSession

#------------------------------------------------------------------------------#
# H E L P E R - F U N C T I O N S
#------------------------------------------------------------------------------#

def trim_str(content: str, empty_string: str) -> str: ...


def repl_comma_with_dot(content: str) -> str: ...


def fit_credits(credits_string: str) -> int: ...


def fit_grade(grade_string: str) -> float: ...


def fit_state(state_string: str) -> Literal["f", "o", "p"]: ...


def add_module_to_dualis_dict(
        m_id: str,
        m_name: str,
        m_href: str,
        m_credits: str,
        m_grade: str,
        m_state: str
) -> DualisModuleDict: ...

#------------------------------------------------------------------------------#
# D U A L I S - I M P O R T E R
#------------------------------------------------------------------------------#

class DualisImporter(ImporterSession):
    url: ClassVar[str]
    params: Dict[str, str]

    def __init__(self) -> None: ...

    async def login(
        self, username: str, password: str) -> Coroutine[Any, Any, Any]: ...

    def _fill_grades_into_dict(
        self, response_text: str) -> Coroutine[Any, Any, Any]: ...

    async def scrape(self) -> Coroutine: ...

    def logout(self) -> None: ...
