from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_service_keyboard(
    full_text: str, base_text: str, without_cleaning_text: str
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=full_text),
                KeyboardButton(text=base_text),
                KeyboardButton(text=without_cleaning_text),
            ],
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def get_room_type_keyboard(
    kitchen_text: str, bedroom_text: str, living_room_text: str
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=kitchen_text),
                KeyboardButton(text=bedroom_text),
                KeyboardButton(text=living_room_text),
            ],
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def get_yes_no_keyboard(yes_text: str, no_text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=yes_text),
                KeyboardButton(text=no_text),
            ]
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
