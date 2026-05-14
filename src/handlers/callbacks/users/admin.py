from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.states.admin import AdminStates
from src.keyboards.inline.admin import (
    get_admin_main_keyboard, 
    get_nodes_keyboard, 
    get_masters_keyboard,
    delete_node,
    delete_master
)

admin_router = Router()

@admin_router.callback_query(AdminStates.admin_panel, F.data == "admin_add_node")
async def callback_admin_add_node(callback: CallbackQuery, state: FSMContext):
    """Add Node button handler"""
    from src.states.setters import set_add_node_state
    
    await callback.answer()
    await set_add_node_state(callback.message, state)
    await callback.message.edit_text(
        _("📋 Nodes list:"),
        reply_markup=get_nodes_keyboard()
    )

@admin_router.callback_query(AdminStates.admin_panel, F.data == "admin_add_master")
async def callback_admin_add_master(callback: CallbackQuery, state: FSMContext):
    """Add Master button handler"""
    from src.states.setters import set_add_master_state
    
    await callback.answer()
    await set_add_master_state(callback.message, state)
    await callback.message.edit_text(
        _("👨‍🔧 Masters list:"),
        reply_markup=get_masters_keyboard()
    )

@admin_router.callback_query(AdminStates.admin_panel, F.data == "admin_exit")
async def callback_admin_exit(callback: CallbackQuery, state: FSMContext):
    """Exit button handler"""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(_("✅ Exited admin panel"))

@admin_router.callback_query(AdminStates.add_node, F.data == "add_new_node")
async def callback_add_new_node(callback: CallbackQuery, state: FSMContext):
    """Add button handler in nodes section"""
    from src.states.setters import set_waiting_node_text_state
    
    await callback.answer()
    await set_waiting_node_text_state(callback.message, state)
    await callback.message.answer(_("✍️ Enter new node name:"))

@admin_router.callback_query(AdminStates.add_node, F.data.startswith("delete_node:"))
async def callback_delete_node(callback: CallbackQuery, state: FSMContext):
    """Node deletion handler"""
    node_text = callback.data.split(":", 1)[1]
    
    if delete_node(node_text):
        await callback.answer(_("Node '{node_text}' deleted").format(node_text=node_text))
        await callback.message.edit_text(
            _("📋 Nodes list:"),
            reply_markup=get_nodes_keyboard()
        )
    else:
        await callback.answer(_("❌ Error deleting node"))

@admin_router.callback_query(AdminStates.add_master, F.data == "add_new_master")
async def callback_add_new_master(callback: CallbackQuery, state: FSMContext):
    """Add button handler in masters section"""
    from src.states.setters import set_waiting_master_text_state
    
    await callback.answer()
    await set_waiting_master_text_state(callback.message, state)
    await callback.message.answer(_("✍️ Enter new master name:"))

@admin_router.callback_query(AdminStates.add_master, F.data.startswith("delete_master:"))
async def callback_delete_master(callback: CallbackQuery, state: FSMContext):
    """Master deletion handler"""
    master_text = callback.data.split(":", 1)[1]
    
    if delete_master(master_text):
        await callback.answer(_("Master '{master_text}' deleted").format(master_text=master_text))
        await callback.message.edit_text(
            _("👨‍🔧 Masters list:"),
            reply_markup=get_masters_keyboard()
        )
    else:
        await callback.answer(_("❌ Error deleting master"))