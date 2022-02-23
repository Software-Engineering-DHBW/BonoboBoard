from typing import Any, ClassVar, Dict, List, TypedDict

from dhbw.util import ImporterSession

class NewContact(TypedDict):
    email: str
    firstName: str
    lastName: str
    jobTitle: str

class ContactsDict(NewContact):
    id: str

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

def _fill_contacts_dict_elem(contact: Dict[str, str]) -> ContactsDict: ...

class ZimbraHandler(ImporterSession):
    accountname: str
    contacts: List[ContactsDict]
    realname: str
    signatures: List[str]
    url: ClassVar[str]

    def __init__(self) -> None: ...

    def login(self, username: str, password: str) -> None: ...

    def scrape(self) -> None: ...

    def get_contacts(self) -> None: ...

    def new_contact(self, contact_dict: NewContact) -> None: ...

    def remove_contact(self, contact_id: str) -> None: ...

    def _create_entities_list(
        self,
        recipients: List[str],
        rec_cc: List[str],
        rec_bcc: List[str]
    ) -> List[Dict[str, str]]: ...

    def _generate_mail(self, mail_dict: SendMailDict) -> Dict[str, Any]: ...

    def send_mail(self, mail_dict: SendMailDict) -> None: ...

    def logout(self) -> None: ...
