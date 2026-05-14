from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    client_name = State()
    date = State()
    client_type = State()
    client_phone = State()
    client_address = State()

    service = State()

    add_room = State()
    add_other_room = State()

    add_block = State()
    add_other_block = State()

    check_list_factors= State()
    add_check_list_factors = State()

    room_cleaning_nodes = State()
    cleaning_node_await_answer = State()

    room_check_list_nodes = State()
    check_list_node_await_answers = State()

    cleaning_node_img_before = State()
    cleaning_node_img_after = State()
    cleaning_node_comment = State()
    cleaning_room_comment = State()

    add_another_room = State()

    check_report = State()
    check_report_add_data = State()

    waiting_for_photo_before = State()
    waiting_for_photo_after = State()
    
    waiting_for_comment = State()
    waiting_for_video = State()

    waiting_work_master = State()
    custom_work_master = State()

