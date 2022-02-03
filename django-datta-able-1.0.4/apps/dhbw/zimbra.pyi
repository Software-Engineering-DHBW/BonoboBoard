from typing import ClassVar, Dict

class ZimbraHandler:
    url: ClassVar[str]
    auth_token: str
    headers: Dict[str, str]

    def __init__(self) -> None: ...

    def drop_header(self, header: str) -> None: ...

    def login(self, username: str, password: str) -> None: ...
