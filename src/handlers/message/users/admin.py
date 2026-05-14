from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.states.admin import AdminStates
from src.keyboards.inline.admin import get_admin_main_keyboard, add_node, add_master

admin_router = Router()


@admin_router.message(AdminStates.waiting_node_text)
async def process_new_node_text(message: Message, state: FSMContext):
    """Processing new node text"""
    from src.keyboards.inline.admin import get_nodes_keyboard
    from src.states.setters import set_add_node_state
    
    node_text = message.text.strip()
    
    if add_node(node_text):
        await message.answer(_("✅ Node '{node_text}' added!").format(node_text=node_text))
    else:
        await message.answer(_("❌ Failed to add node. It may already exist."))
    
    await set_add_node_state(message, state)
    await message.answer(_("📋 Nodes list:"), reply_markup=get_nodes_keyboard())

@admin_router.message(AdminStates.waiting_master_text)
async def process_new_master_text(message: Message, state: FSMContext):
    """Processing new master text"""
    from src.keyboards.inline.admin import get_masters_keyboard
    from src.states.setters import set_add_master_state
    
    master_text = message.text.strip()
    
    if add_master(master_text):
        await message.answer(_("✅ Master '{master_text}' added!").format(master_text=master_text))
    else:
        await message.answer(_("❌ Failed to add master. He may already exist."))
    
    await set_add_master_state(message, state)
    await message.answer(_("👨‍🔧 Masters list:"), reply_markup=get_masters_keyboard())