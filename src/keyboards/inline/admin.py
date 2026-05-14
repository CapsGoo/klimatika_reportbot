from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
import json
import os

# Пути к JSON файлам
NODES_JSON_PATH = "data/nodes.json"
MASTERS_JSON_PATH = "data/masters.json"

def get_json_data(file_path):
    """Reading data from JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if not os.path.exists(file_path):
        # Create empty file if it doesn't exist
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_json_data(file_path, data):
    """Saving data to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin panel main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text=_("➕ Add Node"), callback_data="admin_add_node"),
        InlineKeyboardButton(text=_("👨‍🔧 Add Master"), callback_data="admin_add_master"),
        InlineKeyboardButton(text=_("❌ Exit"), callback_data="admin_exit")
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_nodes_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for managing nodes"""
    builder = InlineKeyboardBuilder()
    
    # Get nodes from JSON
    nodes = get_custom_nodes_list()
    
    # Add buttons for each node
    for node in nodes:
        builder.add(InlineKeyboardButton(
            text=_("❌ {node}").format(node=node), 
            callback_data=f"delete_node:{node}"
        ))
    
    # Add add button
    builder.add(InlineKeyboardButton(text=_("➕ Add"), callback_data="add_new_node"))
    
    builder.adjust(1)
    return builder.as_markup()

def get_masters_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for managing masters"""
    builder = InlineKeyboardBuilder()
    
    # Get masters from JSON
    masters = get_custom_masters_list()
    
    # Add buttons for each master
    for master in masters:
        builder.add(InlineKeyboardButton(
            text=_("❌ {master}").format(master=master), 
            callback_data=f"delete_master:{master}"
        ))
    
    # Add add button
    builder.add(InlineKeyboardButton(text=_("➕ Add"), callback_data="add_new_master"))
    
    builder.adjust(1)
    return builder.as_markup()

def add_node(node_text: str) -> bool:
    """Adding new node"""
    nodes = get_custom_nodes_list()
    
    if node_text.strip() and node_text not in nodes:
        nodes.append(node_text.strip())
        save_json_data(NODES_JSON_PATH, nodes)
        return True
    return False

def delete_node(node_text: str) -> bool:
    """Deleting node"""
    nodes = get_custom_nodes_list()
    
    if node_text in nodes:
        nodes.remove(node_text)
        save_json_data(NODES_JSON_PATH, nodes)
        return True
    return False

def add_master(master_text: str) -> bool:
    """Adding new master"""
    masters = get_custom_masters_list()
    
    if master_text.strip() and master_text not in masters:
        masters.append(master_text.strip())
        save_json_data(MASTERS_JSON_PATH, masters)
        return True
    return False

def delete_master(master_text: str) -> bool:
    """Deleting master"""
    masters = get_custom_masters_list()
    
    if master_text in masters:
        masters.remove(master_text)
        save_json_data(MASTERS_JSON_PATH, masters)
        return True
    return False

# Functions for use in other modules
def get_custom_nodes_list():
    """Getting list of nodes for other modules"""
    return get_json_data(NODES_JSON_PATH)

def get_custom_masters_list():
    """Getting list of masters for other modules"""
    return get_json_data(MASTERS_JSON_PATH)