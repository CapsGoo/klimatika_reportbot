from aiogram import types

from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.misc.getters import get_current_user_report, get_current_user_room
from src.models import Room, Report, Client, CleaningNode,Time
from src.callbackdata import (
    ExtraServiceCB,
    ServiceCB,
    OtherExtraServiceCB,
    ClientCB,
    RoomTypeCB,
    CleaningNodeCB,
    FactorCB,
    BlockTypeCB,
    TimeTypeCB,
    IncompleteNodeCB,
    CheckListNodeCB,
    MasterCB,
    NodeActionCB
)

def get_room_type_keyboard(
    chat_id: int, room_types: list[tuple[str, Room.Type]], other: str,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, room_type in room_types:
        builder.add(
            types.InlineKeyboardButton(
                text=text, callback_data=RoomTypeCB(type=room_type).pack()
            )
        )
    
    builder.add(
        types.InlineKeyboardButton(
            text=other + "➕",
            callback_data=RoomTypeCB(
                action="other_room",
                index=-1,
                type=Room.Type.UNKNOWN,
            ).pack(),
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_datatime_type_keyboard(
    chat_id: int, time_types: list[tuple[str, Time]],
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, time_type in time_types:
        builder.add(
            types.InlineKeyboardButton(
                text=text, callback_data=TimeTypeCB(type=time_type).pack()
            )
        )
    
    builder.adjust(3)
    return builder.as_markup()


def get_block_type_keyboard(
    chat_id: int, block_types: list[tuple[str, Room.Type]],
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, block_type in block_types:
        builder.add(
            types.InlineKeyboardButton(
                text=text, callback_data=BlockTypeCB(type=block_type).pack()
            )
        )
    
    builder.adjust(1)
    return builder.as_markup()


def get_factors_keyboard(
    chat_id: int, block_types: list[tuple[str, Report.Type]],
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, block_type in block_types:
        builder.add(
            types.InlineKeyboardButton(
                text=text, callback_data=FactorCB(type=block_type).pack()
            )
        )
    
    builder.adjust(1)
    return builder.as_markup()


def get_service_keyboard(
    chat_id: int, services: list[tuple[str, Report.Service]]
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, service in services:
        builder.add(
            types.InlineKeyboardButton(
                text=text,
                callback_data=ServiceCB(service=service).pack(),
            )
        )
    builder.adjust(1)
    return builder.as_markup()


def get_cleaning_node_keyboard(
    chat_id: int,
    cleaning_nodes: list[CleaningNode],
    other: str,
    enter: str,
    page: int = 1,
    total_pages: int = 1,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    room = get_current_user_room(chat_id)
    
    # Добавляем кнопки для узлов обслуживания
    for index, cleaning_node in enumerate(cleaning_nodes):
        # Проверяем статус узла по имени (надежнее, чем сравнение объектов)
        status = False
        for node, active in room.default_cleaning_nodes:
            if node.name == cleaning_node.name:
                status = active
                break
        status_text = "✅" if status else "❌"
        adjusted_index = index + 7 if page == 2 else index
        callback_data = CleaningNodeCB(
            action="delete" if status else "add",
            index=adjusted_index,
            page=page,
            type=cleaning_node.type,
        )
        builder.add(
            types.InlineKeyboardButton(
                text=f"{cleaning_node.button_text} {status_text}",
                callback_data=callback_data.pack(),
            )
        )

    # Добавляем кнопки для пользовательских узлов (если они есть на текущей странице)
    for index, cleaning_node in enumerate(room.cleaning_nodes):
        if cleaning_node in cleaning_nodes:
            continue
        callback_data = CleaningNodeCB(
            action="delete",
            index=index,
            type=cleaning_node.type,
        )
        builder.add(
            types.InlineKeyboardButton(
                text=f"{cleaning_node.button_text}",
                callback_data=callback_data.pack(),
            )
        )

    # Добавляем кнопку "Другое"
    builder.add(
        types.InlineKeyboardButton(
            text=other + "➕",
            callback_data=CleaningNodeCB(
                action="add_other",
                index=-1,
                type=CleaningNode.Type.UNKNOWN,
            ).pack(),
        )
    )

    # Добавляем кнопки пагинации, если нужно
    if total_pages > 1:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                types.InlineKeyboardButton(
                    text="⬅️",
                    callback_data=CleaningNodeCB(
                        action="page",
                        page=page-1,
                        index=-2,
                        type=CleaningNode.Type.UNKNOWN
                    ).pack(),
                )
            )
        if page < total_pages:
            pagination_buttons.append(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=CleaningNodeCB(
                        action="page",
                        page=page+1,
                        index=-2,
                        type=CleaningNode.Type.UNKNOWN
                    ).pack(),
                )
            )
        
        if pagination_buttons:
            builder.row(*pagination_buttons)

    # Добавляем кнопку подтверждения
    builder.add(
        types.InlineKeyboardButton(
            text=enter,
            callback_data=CleaningNodeCB(
                action="enter", 
                index=-1, 
                type=CleaningNode.Type.UNKNOWN
            ).pack(),
        )
    )
    
    builder.adjust(1)
    return builder.as_markup()


def get_check_list_node_keyboard(
    chat_id: int,
    cleaning_nodes: list[CleaningNode],
    other: str,
    enter: str
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    room = get_current_user_room(chat_id)
    
    for index, cleaning_node in enumerate(cleaning_nodes):
        # Получаем активность из default_cleaning_nodes
        is_active = False
        extra_factors = None
        
        for node, active in room.default_cleaning_nodes:
            if node.name == cleaning_node.name:
                is_active = active
                extra_factors = node.extra_factors
                break

        # Определяем статус
        if is_active:
            if extra_factors == "immediate":
                status_text = "❗️"
                action = "delete"
            else:  # normal или None
                status_text = "📣"
                action = "immte"
        else:
            status_text = "❌"
            action = "normal"

        callback_data = CheckListNodeCB(
            action=action,
            index=index,
            type=cleaning_node.type,
            node_name=cleaning_node.name,
        )
        builder.add(types.InlineKeyboardButton(
            text=f"{cleaning_node.button_text} {status_text}",
            callback_data=callback_data.pack(),
        ))


    # Добавляем кнопки для пользовательских узлов (если они есть на текущей странице)
    for index, cleaning_node in enumerate(room.cleaning_nodes):
        if cleaning_node in cleaning_nodes:
            continue
        callback_data = CleaningNodeCB(
            action="delete",
            index=index,
            type=cleaning_node.type,
        )
        builder.add(
            types.InlineKeyboardButton(
                text=f"{cleaning_node.name}",
                callback_data=callback_data.pack(),
            )
        )

    # Добавляем кнопку "Другое"
    builder.add(
        types.InlineKeyboardButton(
            text=other + "➕",
            callback_data=CleaningNodeCB(
                action="add_other",
                index=-1,
                type=CleaningNode.Type.UNKNOWN,
            ).pack(),
        )
    )

    # Добавляем кнопку подтверждения
    builder.add(
        types.InlineKeyboardButton(
            text=enter,
            callback_data=CleaningNodeCB(
                action="enter", 
                index=-1, 
                type=CleaningNode.Type.UNKNOWN
            ).pack(),
        )
    )
    
    builder.adjust(1)
    return builder.as_markup()

def get_yes_no_keyboard(chat_id: int, yes: str, no: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=yes, callback_data="yes"))
    builder.add(types.InlineKeyboardButton(text=no, callback_data="no"))
    return builder.as_markup()

# Функция для создания клавиатуры с кнопкой "Пропустить"
def get_skip_keyboard(chat_id: int, skip: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=skip, callback_data="skip"))
    return builder.as_markup()


def get_master_keyboard(
    chat_id: int, 
    masters: list[dict],  # Изменяем на список словарей
    other: str,
    skip: str,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for master_data in masters:  # Работаем со словарями
        builder.add(
            types.InlineKeyboardButton(
                text=master_data["button_text"], 
                callback_data=MasterCB(name=master_data["name"]).pack()
            )
        )

    builder.add(
        types.InlineKeyboardButton(
            text=other,
            callback_data="other"
        )
    )

    builder.add(
        types.InlineKeyboardButton(
            text=skip,
            callback_data="skip"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def check_node_completeness(
        node, 
        room, 
        report
        ) -> tuple[bool, str]:
    missing = []
    

    # Проверка видео в зависимости от типа сервиса
    service_name = report.service.name
    if service_name == "MAINTENANCE":
        if node.photo_before is None or node.photo_after is None:
            missing.append('📷')
        if not room.room_video_id or room.room_video_id.strip() == '':
            missing.append('📹')
        if not room.room_comment or room.room_comment.strip() == '':
            missing.append('💬')
        # if not room.master or room.master.strip() == '':
        #     missing.append('👨🏻‍🔧')


            
    elif service_name == "SERVICE":
        if node.photo_before is None or node.photo_after is None:
            missing.append('📷')
        if not node.video_id or node.video_id.strip() == '':
            missing.append('📹')
        if not node.comment or node.comment.strip() == '':
            missing.append('💬')
        # if not room.master or room.master.strip() == '':
        #     missing.append('👨🏻‍🔧')


    elif service_name == "CHECK_LIST":
        if node.photo_before is None:
            missing.append('📷')    
        # if not room.master or room.master.strip() == '':
        #     missing.append('👨🏻‍🔧')

    return (len(missing) == 0, ' '.join(missing))

from aiogram.utils.i18n import gettext as _



def create_incomplete_nodes_keyboard(
        room,
        report,
        enter: str,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Обрабатываем default nodes (кортежи (CleaningNode, bool))
    for node, is_active in room.default_cleaning_nodes:
        if not is_active:
            continue
            
        is_complete, missing_emojis = check_node_completeness(node, room, report)
        if not is_complete:
            
            # Определяем тип недостающих данных
            missing_types = []
            if '📷' in missing_emojis:
                missing_types.append('p')
            if '📹' in missing_emojis:
                missing_types.append('v')
            if '💬' in missing_emojis:
                missing_types.append('c')
            # if '👨🏻‍🔧' in missing_emojis:
            #     missing_types.append('m')
            
            missing_type = '_'.join(missing_types) if missing_types else 'none'
            
            # Переводим название узла
            translated_node = _(node.button_text)
            btn_text = f"{translated_node} [{missing_emojis}]"
            builder.row(types.InlineKeyboardButton(
                text=btn_text,
                callback_data=IncompleteNodeCB(
                    # room_type=room.room_type,
                    node_name=node.name,  # Оставляем оригинальное имя для callback_data
                    missing_type=missing_type
                ).pack()
            ))

            

    # Обрабатываем custom nodes (CleaningNode)
    for node in room.cleaning_nodes:
        is_complete, missing_emojis = check_node_completeness(node, room, report)
        if not is_complete:
            
            # Определяем тип недостающих данных
            missing_types = []
            if '📷' in missing_emojis:
                missing_types.append('p')
            if '📹' in missing_emojis:
                missing_types.append('v')
            if '💬' in missing_emojis:
                missing_types.append('c')
            # if '👨🏻‍🔧' in missing_emojis:
            #     missing_types.append('m')
            
            missing_type = '_'.join(missing_types) if missing_types else 'none'
            
            # Переводим название узла
            translated_node = _(node.name)
            btn_text = f"{translated_node} [{missing_emojis}]"
            builder.row(types.InlineKeyboardButton(
                text=btn_text,
                callback_data=IncompleteNodeCB(
                    # room_type=room.room_type,
                    node_name=node.name,  # Оставляем оригинальное имя для callback_data
                    missing_type=missing_type
                ).pack()
            ))

    # Добавляем кнопки для мастера
    add_master_text = _("Add room master")
    master_name = room.master if room.master else _("Master")
    
    # Текстовая кнопка (некликабельная)
    builder.row(types.InlineKeyboardButton(
        text=add_master_text + '👨🏻‍🔧:',
        callback_data="ignore"
        )
    )
    
    # Активная кнопка мастера
    builder.row(types.InlineKeyboardButton(
        text=master_name,
        callback_data="add_master"
        )
    )

    # Информационная кнопка
    builder.row(types.InlineKeyboardButton(
        text=_("Do you want to add room?"),
        callback_data="ignore"
        )
    )
    

    # Кнопки да/нет в одном ряду
    builder.row(
        types.InlineKeyboardButton(text=_("yes"), callback_data="yes"),
        types.InlineKeyboardButton(text=_("no"), callback_data="no")
    )

    return builder.as_markup()