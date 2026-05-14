from typing import BinaryIO
from aiogram import types, Bot
from typing import List, Tuple
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Time:
    class Type(str, Enum):
        UNKNOWN = "Unknown"
        EREYESTERDEY = "2 days ago"
        YESTERDAY = "Yesterday"
        TODAY = "Today"

        def __str__(self) -> str:
            return str(self.value)

        def for_button(self, text: str) -> Tuple[str, ...]:
            return (text, self)
