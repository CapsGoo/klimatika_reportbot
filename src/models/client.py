from dataclasses import dataclass
from enum import Enum


@dataclass
class Client:
    class Type(str, Enum):
        UNKNOWN = ""
        OWNER = "OWNER"
        TENANT = "TENANT"

        def __str__(self) -> str:
            return str(self.value)

        def for_button(self, text: str) -> tuple[str, Enum]:
            return (text, self.value)

    name: str = ""
    phone: str = ""
    type: Type = Type.UNKNOWN
    address: str = ""
