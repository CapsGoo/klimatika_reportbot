from typing import BinaryIO
from aiogram import types, Bot
from typing import List, Tuple
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Block:
    class Type(str, Enum):
        UNKNOWN = "Unknown"
        INDOOR = "In door block"
        OUTDOOR = "Out door block"
        OTHER = "Other"

        def __str__(self) -> str:
            return str(self.value)

        def for_button(self, text: str) -> Tuple[str, ...]:
            return (text, self)


