# from aiogram import Router, types, F
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
# from aiogram.utils.i18n import gettext as _

# from src.models import Room, CleaningNode
# from src.states.form import Form

# import src.misc.getters as get
# from src.states import setters as set_state

# from loader import users

# router = Router()


# @router.message(Form.repair_img_before, F.photo)
# async def repair_img_before(message: types.Message, state: FSMContext) -> None:
#     room = get.get_current_user_room(message.chat.id)
#     room.last_cleaning_node.photo_before = get.get_photo(message.photo)

#     await set_state.set_repair_img_after_state(message, state)


# @router.message(Form.repair_img_after, F.photo)
# async def repair_img_after(message: types.Message, state: FSMContext) -> None:
#     room = get.get_current_user_room(message.chat.id)
#     room.last_cleaning_node.photo_after = get.get_photo(message.photo)

#     await set_state.set_add_repair_unit_state(message, state)
