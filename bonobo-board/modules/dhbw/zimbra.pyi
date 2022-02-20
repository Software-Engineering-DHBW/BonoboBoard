from typing import Any, ClassVar, Dict, List, TypedDict

from dhbw.util import ImporterSession

class SendMailDict(TypedDict):
    recipients: List[str]
    rec_cc: List[str]
    rec_bcc: List[str]
    subject: str
    cttype: str
    content: str

def _entity_list(
    in_list: List[str],
    out_list: List[Dict[str, str]],
    in_type: str
) -> List[Dict[str, str]]: ...

class ZimbraHandler(ImporterSession):
    accountname: str
    contacts: List[str]
    realname: str
    signatures: List[str]
    url: ClassVar[str]

    def __init__(self) -> None: ...

    def drop_header(self, header: str) -> None: ...

    def login(self, username: str, password: str) -> None: ...

    def scrape(self) -> None: ...

    def _create_entities_list(
        self,
        recipients: List[str],
        rec_cc: List[str],
        rec_bcc: List[str]
    ) -> List[Dict[str, str]]: ...

    def _generate_mail(self, mail_dict: SendMailDict) -> Dict[str, Any]: ...

    def send_mail(self, mail_dict: SendMailDict) -> None: ...

    def logout(self) -> None: ...
