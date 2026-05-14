from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.models.report import Report
from src.states.form import Form

import src.misc.getters as get
from src.states import setters as set_state
from loader import users

# Импорты для админ панели - исправленные пути
from src.states.admin import AdminStates
from src.keyboards.inline.admin import get_admin_main_keyboard
from src.states.setters import set_admin_panel_state

router = Router()

@router.message(Command(commands=["start"]))
async def command_start(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    users[message.chat.id] = Report()
    user_locale = message.from_user.language_code or 'ru'  # Получаем язык пользователя
    await state.update_data(language=user_locale)
    await message.answer(
        _("Hi! {first_name} {last_name}").format(
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    )

    await set_state.set_client_name_state(message, state)

@router.message(Command(commands=["admin"]))
async def admin_command(message: types.Message, state: FSMContext):
    """Admin command handler"""
    await set_admin_panel_state(message, state)
    await message.answer(
        _("🔧 Admin panel"),
        reply_markup=get_admin_main_keyboard()
    )