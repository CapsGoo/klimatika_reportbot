# from aiogram import Router, types, F
# from aiogram.fsm.context import FSMContext


# from src.states import Form
# from src.states import setters as set_state

# import src.misc.getters as get

# from src.models import CleaningNode



# router = Router()


# @router.callback_query(Form.add_repair_unit, F.data == "yes")
# async def callback_add_repair_unit_yes(
#     callback: types.CallbackQuery, state: FSMContext
# ) -> None:
#     await callback.answer()
#     room = get.get_current_user_room(callback.message.chat.id)
#     room.add_node(CleaningNode("", type=CleaningNode.Type.OTHER))
#     await set_state.set_repair_img_before_state(callback.message, state)


# @router.callback_query(Form.add_repair_unit, F.data == "no")
# async def callback_add_repair_unit_yes(
#     callback: types.CallbackQuery, state: FSMContext
# ) -> None:
#     await callback.answer()
#     await set_state.set_add_room_state(callback.message, state)
