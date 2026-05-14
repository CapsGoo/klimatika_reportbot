from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    admin_panel = State()
    add_node = State()
    add_master = State()
    waiting_node_text = State()
    waiting_master_text = State()