import re
import dateparser
from datetime import datetime


def is_valid_name(text: str | None) -> bool:
    if text is None:
        return False
    return True


def is_valid_date(text: str | None) -> bool:
    text_formated = text.replace(".", " ").replace(":", " ").replace("/", " ")
    text_list = text_formated.split()
    if len(text_list) < 3:
        return False

    if any(not text.isnumeric() for text in text_list):
        return False

    date_list = list(map(int, text_list))
    if any(num <= 0 for num in date_list):
        return False

    if date_list[0] > 31 or date_list[1] > 12 or date_list[2] > datetime.now().year:
        return False

    date = dateparser.parse(
        text_formated,
        settings={
            "DATE_ORDER": "DMY",
            "REQUIRE_PARTS": ["day", "month", "year"],
            "STRICT_PARSING": True,
        },
    )
    if date is None:
        return False

    return True


def is_valid_phone(text: str | None) -> bool:
    if text is None:
        return False

    text = text.replace(" ", "").replace("+", "").replace("-", "")
    if not text.isdigit():
        return False

    return True


def is_valid_email(text: str | None) -> bool:
    if text is None:
        return False

    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if not re.fullmatch(regex, text):
        return False

    return True


def is_valid_address(text: str | None):
    if text is None:
        return False
    return True


def is_valid_helped_with(text: str | None) -> bool:
    if text is None:
        return False

    if len(text) > 50:
        return False

    return True


def is_valid_cleaned(text: str | None) -> bool:
    if text is None:
        return False

    if len(text) > 270:
        return False

    return True


def is_valid_rooms_count(text: str | None) -> bool:
    if text is None:
        return False

    if not text.isdigit():
        return False

    if int(text) <= 0:
        return False
    return True


def is_valid_room_type(text: str | None) -> bool:
    if text is None:
        return False
    return True


def is_valid_room_object(text: str | None) -> bool:
    if text is None:
        return False
    if len(text) > 25:
        return False

    return True
