from aiogram import types
from datetime import datetime
import dateparser

from loader import users

from typing import Optional, Tuple
from src.models.room import Room
from src.models.report import Report

from src.misc.utils import slugify


def get_date(text: str | None) -> datetime:
    if text is None:
        return datetime.now()
    date = dateparser.parse(text, settings={"DATE_ORDER": "DMY"})
    if date is None:
        return datetime.now()
    return date


def get_name(text: str | None) -> str:
    if text is None:
        return ""
    return text 


def get_email(text: str | None) -> str:
    if text is None:
        return ""
    return text


def get_phone(text: str | None) -> str:
    if text is None:
        return ""

    return text.replace(" ", "").replace("+", "").replace("-", "")


def get_address(text: str | None) -> str:
    if text is None:
        return ""
    return text


def get_service(text: str | None) -> str:
    if text is None:
        return Report.Service.UNKNOWN
    return Report.Service(text)


def get_rooms_count(text: str | None) -> int:
    if text is None:
        return 0
    return int(text)


def get_room_object(text: str | None) -> str:
    if text is None:
        return ""
    return text


def get_current_user_report(chat_id: int) -> Report:
    return users[chat_id]


def get_current_user_room(chat_id: int) -> Room:
    report = get_current_user_report(chat_id)
    return report.rooms[-1]


def get_photo(photos: list[types.PhotoSize] | None) -> list[types.PhotoSize] | None:
    if photos is None:
        return None
    return photos[-1]
