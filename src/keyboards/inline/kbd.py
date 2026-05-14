from aiogram.utils.i18n import gettext as _
from aiogram import types
from src.models import Room, Report, Client, CleaningNode, Block,Time
from .form import (
    get_service_keyboard,
    get_yes_no_keyboard,
    get_room_type_keyboard,
    get_cleaning_node_keyboard,
    get_factors_keyboard,
    get_skip_keyboard,
    get_block_type_keyboard,
    get_datatime_type_keyboard,
    create_incomplete_nodes_keyboard,
    get_check_list_node_keyboard,
    get_master_keyboard

)

from src.misc import getters as get 
from src.keyboards.inline.admin import get_custom_nodes_list, get_custom_masters_list

async def send_room_type_keyboard(message: types.Message):
    await message.answer(
        _("Select room type:"),
        reply_markup=get_room_type_keyboard(
            message.chat.id,
            [
                Room.Type.KITCHEN.for_button(_("Kitchen")),
                Room.Type.BEDROOM.for_button(_("Bedroom")),
                Room.Type.LIVING_ROOM.for_button(_("Living Room")),
                Room.Type.MASTER_ROOM.for_button(_("Master bedroom")),
                Room.Type.KIDS_ROOM.for_button(_("Kids bedroom")),
                Room.Type.GUEST_ROOM.for_button(_("Guest bedroom")),
                Room.Type.MAIDS_ROOM.for_button(_("Maids bedroom")),
                Room.Type.CABINET_ROOM.for_button(_("Cabinet room")),
                Room.Type.GYM.for_button(_("Gym"))
            ],
        other=_("Other"),
        ),
    )
async def send_datetime_type_keyboard(message: types.Message):
    await message.answer(
        _("Enter date of visit in format DAY MONTH YEAR.\n\nFor example: 1 12 2022 (December the 1st, 2022)"),
        reply_markup=get_datatime_type_keyboard(
            message.chat.id,
            [   
                Time.Type.EREYESTERDEY.for_button(_("2 days ago")),
                Time.Type.YESTERDAY.for_button(_("Yesterday")),
                Time.Type.TODAY.for_button(_("Today")),
            ],
        ),
    )

    
async def send_block_type_keyboard(message: types.Message):
    await message.answer(
        _("Select unit type:"),
        reply_markup=get_block_type_keyboard(
            message.chat.id,
            [   
                Block.Type.INDOOR.for_button(_("Indoor unit")),
                Block.Type.OUTDOOR.for_button(_("Outdoor unit")),
                Block.Type.OTHER.for_button(_("Other")),
            ],
        ),
    )


async def send_service_keyboard(message: types.Message):
    await message.answer(
        _("Choose service:"),
        reply_markup=get_service_keyboard(
            message.chat.id,
            [
                Report.Service.SERVICE.for_button(_("Service")),
                Report.Service.MAINTENANCE.for_button(_("Maintenance")),
                Report.Service.CHECK_LIST.for_button(_("Check list")),

            ],
        ),
    )



async def edit_service_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose service:"),
        reply_markup=get_service_keyboard(
            message.chat.id,
            [
                Report.Service.SERVICE.for_button(_("Service")),
                Report.Service.MAINTENANCE.for_button(_("Maintenance")),
                Report.Service.CHECK_LIST.for_button(_("Check list")),
            ],
        ),
    )

async def send_yes_no_keboard(message: types.Message, text: str):
    await message.answer(
        text=text,
        reply_markup=get_yes_no_keyboard(message.chat.id, yes=_("Yes"), no=_("No")),
    )

# Функция для отправки сообщения с клавиатурой "Пропустить"
async def send_skip_keyboard(message: types.Message, text: str):
    await message.answer(
        text=text,
        reply_markup=get_skip_keyboard(message.chat.id,skip=_("Skip"))
    )

async def send_service_indoor_node_keyboard(message: types.Message):
    await message.answer(
        _("Choose cleaning nodes"),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            [
            CleaningNode("valve", type=CleaningNode.Type.DEFAULT, button_text=_("valve")),
            CleaningNode("аctuator", type=CleaningNode.Type.DEFAULT, button_text=_("аctuator")),
            CleaningNode("insulation fixing", type=CleaningNode.Type.DEFAULT, button_text=_("insulation fixing")),
            CleaningNode("indoor unit condenser replacement", type=CleaningNode.Type.DEFAULT, button_text=_("indoor unit condenser replacement")),
            CleaningNode("thermostat adjustment", type=CleaningNode.Type.DEFAULT, button_text=_("thermostat adjustment")),
            CleaningNode("thermostat replacement", type=CleaningNode.Type.DEFAULT, button_text=_("thermostat replacement")),
            CleaningNode("motor replacement ", type=CleaningNode.Type.DEFAULT, button_text=_("motor replacement")),
            CleaningNode("blower replacement", type=CleaningNode.Type.DEFAULT, button_text=_("blower replacement")),
            CleaningNode("filter replacement/installation", type=CleaningNode.Type.DEFAULT, button_text=_("filter replacement/installation"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def edit_service_indoor_node_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose service nodes"),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            [
            CleaningNode("valve", type=CleaningNode.Type.DEFAULT, button_text=_("valve")),
            CleaningNode("аctuator", type=CleaningNode.Type.DEFAULT, button_text=_("аctuator")),
            CleaningNode("insulation fixing", type=CleaningNode.Type.DEFAULT, button_text=_("insulation fixing")),
            CleaningNode("indoor unit condenser replacement", type=CleaningNode.Type.DEFAULT, button_text=_("indoor unit condenser replacement")),
            CleaningNode("thermostat adjustment", type=CleaningNode.Type.DEFAULT, button_text=_("thermostat adjustment")),
            CleaningNode("thermostat replacement", type=CleaningNode.Type.DEFAULT, button_text=_("thermostat replacement")),
            CleaningNode("motor replacement ", type=CleaningNode.Type.DEFAULT, button_text=_("motor replacement")),
            CleaningNode("blower replacement", type=CleaningNode.Type.DEFAULT, button_text=_("blower replacement")),
            CleaningNode("filter replacement/installation", type=CleaningNode.Type.DEFAULT, button_text=_("filter replacement/installation"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def send_service_outdoor_node_keyboard(message: types.Message):
    await message.answer(
        _("Choose cleaning nodes"),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            [
            CleaningNode("compressor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("compressor replacement")),
            CleaningNode("starter replacement", type=CleaningNode.Type.DEFAULT, button_text=_("starter replacement")),
            CleaningNode("motor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("motor replacement")),
            CleaningNode("capacitor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("capacitor replacement")),
            CleaningNode("fan motor", type=CleaningNode.Type.DEFAULT, button_text=_("fan motor")),
            CleaningNode("electrical checking and tightening", type=CleaningNode.Type.DEFAULT, button_text=_("electrical checking and tightening")),
            CleaningNode("gas pressure checking", type=CleaningNode.Type.DEFAULT, button_text=_("gas pressure checking"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def edit_service_outdoor_node_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose service nodes"),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            [
            CleaningNode("compressor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("compressor replacement")),
            CleaningNode("starter replacement", type=CleaningNode.Type.DEFAULT, button_text=_("starter replacement")),
            CleaningNode("motor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("motor replacement")),
            CleaningNode("capacitor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("capacitor replacement")),
            CleaningNode("fan motor", type=CleaningNode.Type.DEFAULT, button_text=_("fan motor")),
            CleaningNode("electrical checking and tightening", type=CleaningNode.Type.DEFAULT, button_text=_("electrical checking and tightening")),
            CleaningNode("gas pressure checking", type=CleaningNode.Type.DEFAULT, button_text=_("gas pressure checking"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def send_service_other_node_keyboard(message: types.Message):
    await message.answer(
        _("Choose cleaning nodes"),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            [
            CleaningNode("water heater replacement", type=CleaningNode.Type.DEFAULT, button_text=_("water heater replacement")),
            CleaningNode("pump replacement", type=CleaningNode.Type.DEFAULT, button_text=_("pump replacement")),
            CleaningNode("FAHU motor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("FAHU motor replacement")),
            CleaningNode("FAHU belt replacement", type=CleaningNode.Type.DEFAULT, button_text=_("FAHU belt replacement")),
            CleaningNode("high efficiency filter replacement", type=CleaningNode.Type.DEFAULT, button_text=_("high efficiency filter replacement"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def edit_service_other_node_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose service nodes"),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            [
            CleaningNode("water heater replacement", type=CleaningNode.Type.DEFAULT, button_text=_("water heater replacement")),
            CleaningNode("pump replacement", type=CleaningNode.Type.DEFAULT, button_text=_("pump replacement")),
            CleaningNode("FAHU motor replacement", type=CleaningNode.Type.DEFAULT, button_text=_("FAHU motor replacement")),
            CleaningNode("FAHU belt replacement", type=CleaningNode.Type.DEFAULT, button_text=_("FAHU belt replacement")),
            CleaningNode("high efficiency filter replacement", type=CleaningNode.Type.DEFAULT, button_text=_("high efficiency filter replacement"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def send_maintenance_node_keyboard(message: types.Message, page: int = 1):
    # Разделяем узлы на две страницы
    nodes = [
        CleaningNode("grills", type=CleaningNode.Type.DEFAULT, button_text=_("grills")),
        CleaningNode("duct", type=CleaningNode.Type.DEFAULT, button_text=_("duct")),
        CleaningNode("pan", type=CleaningNode.Type.DEFAULT, button_text=_("pan")),
        CleaningNode("evaporator", type=CleaningNode.Type.DEFAULT,button_text=_("evaporator")),
        CleaningNode("blower", type=CleaningNode.Type.DEFAULT, button_text=_("blower")),
        CleaningNode("filter", type=CleaningNode.Type.DEFAULT, button_text=_("filter")),
        CleaningNode("ceiling area", type=CleaningNode.Type.DEFAULT, button_text=_("ceiling area"))
        ]
    
    
    custom_nodes = CleaningNode.create_custom_nodes_list(get_custom_nodes_list())
    
    current_nodes = nodes if page == 1 else custom_nodes
    
    await message.answer(
        _("Choose maintenance nodes (Page {}/2)").format(page),
        reply_markup=get_cleaning_node_keyboard(
            message.chat.id,
            current_nodes,
            other=_("Other"),
            enter=_("Enter"),
            page=page,
            total_pages=2
        ),
    )

async def edit_maintenance_node_keyboard(message: types.Message, page: int = 1):

    nodes = [
        CleaningNode("grills", type=CleaningNode.Type.DEFAULT, button_text=_("grills")),
        CleaningNode("duct", type=CleaningNode.Type.DEFAULT, button_text=_("duct")),
        CleaningNode("pan", type=CleaningNode.Type.DEFAULT, button_text=_("pan")),
        CleaningNode("evaporator", type=CleaningNode.Type.DEFAULT,button_text=_("evaporator")),
        CleaningNode("blower", type=CleaningNode.Type.DEFAULT, button_text=_("blower")),
        CleaningNode("filter", type=CleaningNode.Type.DEFAULT, button_text=_("filter")),
        CleaningNode("ceiling area", type=CleaningNode.Type.DEFAULT, button_text=_("ceiling area"))
        ]
    
    custom_nodes = CleaningNode.create_custom_nodes_list(get_custom_nodes_list())
    
    current_nodes = nodes if page == 1 else custom_nodes

    keyboard = get_cleaning_node_keyboard(
        message.chat.id,
        current_nodes,
        other=_("Other"),
        enter=_("Enter"),
        page=page,
        total_pages=2
    )
    
    await message.edit_text(
        _("Choose maintenance nodes (Page {}/2)").format(page),
        reply_markup=keyboard,
    )


async def send_factors_keyboard(message: types.Message):
    await message.answer(
        _("Select block type:"),
        reply_markup=get_factors_keyboard(
            message.chat.id,
            [   
                Report.Type.FULL_MAINTENANCE.for_button(_("Full Maintenance")),
                Report.Type.SUPPORT.for_button(_("Support")),
                Report.Type.OTHER.for_button(_("Other")),
            ],
        ),
    )



async def send_check_list_full_maintenance_node_keyboard(message: types.Message):
    await message.answer(
        _("Choose completed work:\n"
        "❗️ - recommendation for action immediately \n" \
        "📣 - recommendation for actions in the next service\n"\
        "❌ - no action recommendation selected"
        ),
        reply_markup=get_check_list_node_keyboard(
            message.chat.id,
            [
            CleaningNode("Disassembling and cleaning the grills", type=CleaningNode.Type.DEFAULT, button_text=_("Disassembling and cleaning the grills")),
            CleaningNode("Duct cleaning and desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Duct cleaning and desinfection")),
            CleaningNode("Evaporator cleaning and desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Evaporator cleaning and desinfection")),
            CleaningNode("Blower cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Blower cleaning")),
            CleaningNode("Filter cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Filter cleaning")),
            CleaningNode("Installation of additional filters", type=CleaningNode.Type.DEFAULT, button_text=_("Installation of additional filters")),
            CleaningNode("Drainage cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Drainage cleaning")),
            CleaningNode("Outside unit cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("Outside unit cleaning (if required)")),
            CleaningNode("Pcb cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Pcb cleaning")),
            CleaningNode("Pulling electrical fasteners", type=CleaningNode.Type.DEFAULT, button_text=_("Pulling electrical fasteners"))
            ],  
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def edit_check_list_full_maintenance_node_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose completed work:\n"
        "❗️ - recommendation for action immediately \n" \
        "📣 - recommendation for actions in the next service\n"\
        "❌ - no action recommendation selected"
        ),
        reply_markup=get_check_list_node_keyboard(
            message.chat.id,
            [
            CleaningNode("Disassembling and cleaning the grills", type=CleaningNode.Type.DEFAULT, button_text=_("Disassembling and cleaning the grills")),
            CleaningNode("Duct cleaning and desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Duct cleaning and desinfection")),
            CleaningNode("Evaporator cleaning and desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Evaporator cleaning and desinfection")),
            CleaningNode("Blower cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Blower cleaning")),
            CleaningNode("Filter cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Filter cleaning")),
            CleaningNode("Installation of additional filters", type=CleaningNode.Type.DEFAULT, button_text=_("Installation of additional filters")),
            CleaningNode("Drainage cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Drainage cleaning")),
            CleaningNode("Outside unit cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("Outside unit cleaning (if required)")),
            CleaningNode("Pcb cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Pcb cleaning")),
            CleaningNode("Pulling electrical fasteners", type=CleaningNode.Type.DEFAULT, button_text=_("Pulling electrical fasteners"))
            ],  
            other=_("Other"),
            enter=_("Enter"),
        ),
    )



async def send_check_list_support_node_keyboard(message: types.Message):
    await message.answer(
        _("Choose completed work:\n"
        "❗️ - recommendation for action immediately \n" \
        "📣 - recommendation for actions in the next service\n"\
        "❌ - no action recommendation selected"
        ),
        reply_markup=get_check_list_node_keyboard(
            message.chat.id,
            [
            CleaningNode("Checking for mold on the grill", type=CleaningNode.Type.DEFAULT, button_text=_("Checking for mold on the grill")),
            CleaningNode("Duct desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Duct desinfection")),
            CleaningNode("Evaporator desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Evaporator desinfection")),
            CleaningNode("Filter cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Filter cleaning")),
            CleaningNode("Installation of additional filters", type=CleaningNode.Type.DEFAULT, button_text=_("Installation of additional filters")),
            CleaningNode("Pan cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Pan cleaning")),
            CleaningNode("Drainage cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Drainage cleaning")),
            CleaningNode("Outside unit cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("Outside unit cleaning (if required)")),
            CleaningNode("pcb cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("pcb cleaning (if required)")),
            CleaningNode("Pulling electrical fasteners (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("Pulling electrical fasteners (if required)"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def edit_check_list_support_node_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose completed work:\n"
        "❗️ - recommendation for action immediately \n" \
        "📣 - recommendation for actions in the next service\n"\
        "❌ - no action recommendation selected"
        ),
        reply_markup=get_check_list_node_keyboard(
            message.chat.id,
            [
            CleaningNode("Checking for mold on the grill", type=CleaningNode.Type.DEFAULT, button_text=_("Checking for mold on the grill")),
            CleaningNode("Duct desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Duct desinfection")),
            CleaningNode("Evaporator desinfection", type=CleaningNode.Type.DEFAULT, button_text=_("Evaporator desinfection")),
            CleaningNode("Filter cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Filter cleaning")),
            CleaningNode("Installation of additional filters", type=CleaningNode.Type.DEFAULT, button_text=_("Installation of additional filters")),
            CleaningNode("Pan cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Pan cleaning")),
            CleaningNode("Drainage cleaning", type=CleaningNode.Type.DEFAULT, button_text=_("Drainage cleaning")),
            CleaningNode("Outside unit cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("Outside unit cleaning (if required)")),
            CleaningNode("pcb cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("pcb cleaning (if required)")),
            CleaningNode("Pulling electrical fasteners (if required)", type=CleaningNode.Type.DEFAULT, button_text=_("Pulling electrical fasteners (if required)"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def send_check_list_other_node_keyboard(message: types.Message):
    await message.answer(
        _("Choose completed work:\n"
        "❗️ - recommendation for action immediately \n" \
        "📣 - recommendation for actions in the next service\n"\
        "❌ - no action recommendation selected"
        ),
        reply_markup=get_check_list_node_keyboard(
            message.chat.id,
            [
            CleaningNode("Evaporator service Fresh Air Unit(FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Evaporator service Fresh Air Unit(FHU)")),
            CleaningNode("Blower service (FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Blower service (FHU)")),
            CleaningNode("Filter cleaning (FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Filter cleaning (FHU)")),
            CleaningNode("Fine filter (FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Fine filter (FHU)")),
            CleaningNode("Belt FHU", type=CleaningNode.Type.DEFAULT, button_text=_("Belt FHU")),
            CleaningNode("Exhaust fan", type=CleaningNode.Type.DEFAULT, button_text=_("Exhaust fan"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )


async def edit_check_list_other_node_keyboard(message: types.Message):
    await message.edit_text(
        _("Choose completed work:\n"
        "❗️ - recommendation for action immediately \n" \
        "📣 - recommendation for actions in the next service\n"\
        "❌ - no action recommendation selected"
        ),
        reply_markup=get_check_list_node_keyboard(
            message.chat.id,
            [
            CleaningNode("Evaporator service Fresh Air Unit(FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Evaporator service Fresh Air Unit(FHU)")),
            CleaningNode("Blower service (FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Blower service (FHU)")),
            CleaningNode("Filter cleaning (FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Filter cleaning (FHU)")),
            CleaningNode("Fine filter (FHU)", type=CleaningNode.Type.DEFAULT, button_text=_("Fine filter (FHU)")),
            CleaningNode("Belt FHU", type=CleaningNode.Type.DEFAULT, button_text=_("Belt FHU")),
            CleaningNode("Exhaust fan", type=CleaningNode.Type.DEFAULT, button_text=_("Exhaust fan"))
            ],
            other=_("Other"),
            enter=_("Enter"),
        ),
    )



async def send_report_keyboard(message: types.Message):
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)

    # Don't translate the variable directly, use string formatting
    keyboard = create_incomplete_nodes_keyboard(
        room,
        report,
        _("Enter")
    )
    
    # Translate the template string and format it with the actual room name
    await message.answer(
        _("Room: {room_name}\n\nServiced nodes:\nNO photo - 📷\nNO video - 📹\nNO comment - 💬\n\nTap to node for change").format(
            room_name=room.room_object
        ),
        reply_markup=keyboard
    )

async def send_master_keyboard(message: types.Message):
    master_nodes = Report.create_custom_nodes_list(get_custom_masters_list())

    keyboard = get_master_keyboard(
        message.chat.id,
        master_nodes,
        other=_("Other"),
        skip =_("Skip")

    )
    await message.answer(
        _("Select report master:"),
        reply_markup=keyboard,
    )