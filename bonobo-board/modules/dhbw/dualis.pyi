from typing import ClassVar, Dict, Literal
from .util import DualisModuleDict, ImporterSession


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


class DualisImporter(ImporterSession):
    url: ClassVar[str]
    params: Dict[str, str]

    def __init__(self) -> None: ...

    def login(self, username: str, password: str) -> None: ...

    def _fill_grades_into_dict(self, response_text: str) -> None: ...

    def scrape(self) -> None: ...

    def logout(self) -> None: ...
