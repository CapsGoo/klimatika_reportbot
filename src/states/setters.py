from aiogram import types
from aiogram.fsm.context import FSMContext

from aiogram.utils.i18n import gettext as _

from src.states import Form
from src.keyboards import inline
from src.misc import getters as get

from src.models import Report, CleaningNode
from src.models.cleaningnode import DEFAULT_INDOOR_SERVICE_NODES,DEFAULT_OUTDOOR_SERVICE_NODES,DEFAULT_OTHER_SERVICE_NODES,DEFAULT_MAINTENANCE_NODES,DEFAULT_FULL_MAINTENANCE_CHECK_LIST_NODE,DEFAULT_SUPPORT_CHECK_LIST_NODE,DEFAULT_OTHER_CHECK_LIST_NODE
from .admin import AdminStates

from src.keyboards.inline.admin import get_custom_nodes_list

async def set_client_name_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.client_name)
    await message.answer(_("Enter clients Name"))

async def set_date_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.date)
    await inline.send_datetime_type_keyboard(message)

async def set_client_phone_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.client_phone)
    await message.answer(_("Enter Phone number"))

async def set_client_address_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.client_address)
    await message.answer(_("Enter client address:"))

async def set_service_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.service)
    await inline.send_service_keyboard(message)

#ADD room
async def set_room_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.add_room)
    await inline.send_room_type_keyboard(message) 

# ADD BLOCK
async def set_block_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.add_block)
    await inline.send_block_type_keyboard(message) 

async def set_check_list_factors_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.check_list_factors)
    await inline.send_factors_keyboard(message)

# NO work
async def set_room_service_nodes_state(message: types.Message, state: FSMContext):
    set_indoor_service_nodes(message)
    await state.set_state(Form.room_cleaning_nodes)
    await inline.send_service_indoor_node_keyboard(message)

async def set_room_indoor_service_nodes_state(message: types.Message, state: FSMContext):
    set_indoor_service_nodes(message)
    await state.set_state(Form.room_cleaning_nodes)
    await inline.send_service_indoor_node_keyboard(message)

async def set_room_outdoor_service_nodes_state(message: types.Message, state: FSMContext):
    set_outdoor_service_nodes(message)
    await state.set_state(Form.room_cleaning_nodes)
    await inline.send_service_outdoor_node_keyboard(message)

async def set_room_other_service_nodes_state(message: types.Message, state: FSMContext):
    set_other_service_nodes(message)
    await state.set_state(Form.room_cleaning_nodes)
    await inline.send_service_other_node_keyboard(message)

async def set_room_maintenance_nodes_state(message: types.Message, state: FSMContext):
    set_default_maintenance_nodes(message)
    await state.set_state(Form.room_cleaning_nodes)
    await inline.send_maintenance_node_keyboard(message)

async def set_check_list_full_maintenancee_nodes_state(message: types.Message, state: FSMContext):
    set_check_list_full_maintenancee_nodes(message)
    await state.set_state(Form.room_check_list_nodes)
    await inline.send_check_list_full_maintenance_node_keyboard(message)

async def set_check_list_support_nodes_state(message: types.Message, state: FSMContext):
    set_check_list_support_nodes(message)
    await state.set_state(Form.room_check_list_nodes)
    await inline.send_check_list_support_node_keyboard(message)

async def set_check_list_other_nodes_state(message: types.Message, state: FSMContext):
    set_check_list_other_nodes(message)
    await state.set_state(Form.room_check_list_nodes)
    await inline.send_check_list_other_node_keyboard(message)

async def set_check_report_state(message: types.Message, state: FSMContext):
    await state.set_state(Form.check_report)
    await inline.send_report_keyboard(message)

async def set_img_before_state(message: types.Message, state: FSMContext) -> None:
    room = get.get_current_user_room(message.chat.id)
    translated_node = _(room.current_node.button_text)
    await state.set_state(Form.cleaning_node_img_before)
    await inline.send_skip_keyboard(message, _("Send photo BEFORE for {}").format(translated_node))

async def set_img_after_state(message: types.Message, state: FSMContext) -> None:
    room = get.get_current_user_room(message.chat.id)
    translated_node = _(room.current_node.button_text)
    await state.set_state(Form.cleaning_node_img_after)
    await inline.send_skip_keyboard(message, _("Send photo AFTER for {}").format(translated_node))

async def set_work_master_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_work_master)
    await inline.send_master_keyboard(message)

async def set_admin_panel_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.admin_panel)

async def set_add_node_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_node)

async def set_add_master_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_master)

async def set_waiting_node_text_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.waiting_node_text)

async def set_waiting_master_text_state(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.waiting_master_text)

def set_indoor_service_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    # Полная переинициализация узлов
    room.default_cleaning_nodes = [[node, True] for node in DEFAULT_INDOOR_SERVICE_NODES]

def set_outdoor_service_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    # Полная переинициализация узлов
    room.default_cleaning_nodes = [[node, True] for node in DEFAULT_OUTDOOR_SERVICE_NODES]

def set_other_service_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    # Полная переинициализация узлов
    room.default_cleaning_nodes = [[node, True] for node in DEFAULT_OTHER_SERVICE_NODES]

def set_default_maintenance_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    room.default_cleaning_nodes = [[node, True] for node in (DEFAULT_MAINTENANCE_NODES 
        + CleaningNode.create_custom_nodes_list(get_custom_nodes_list()))]

def set_check_list_full_maintenancee_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    # Полная переинициализация узлов
    room.default_cleaning_nodes = [[node, True] for node in DEFAULT_FULL_MAINTENANCE_CHECK_LIST_NODE]

def set_check_list_support_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    # Полная переинициализация узлов
    room.default_cleaning_nodes = [[node, True] for node in DEFAULT_SUPPORT_CHECK_LIST_NODE]

def set_check_list_other_nodes(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    # Полная переинициализация узлов
    room.default_cleaning_nodes = [[node, True] for node in DEFAULT_OTHER_CHECK_LIST_NODE]








