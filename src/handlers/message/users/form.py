from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from typing import List, Tuple
import src.keyboards.inline as inline

import time, os 

from src.states.form import Form
from src.models import Report, Room, Client, CleaningNode
import src.misc.validators as vld
import src.misc.getters as get
from src.states import setters as set_state

from src.handlers.callbacks.users.form import send_pdf_report
form_router = Router()


@form_router.message(Form.client_name, F.text)
async def process_name(message: types.Message, state: FSMContext) -> None:
    if not vld.is_valid_name(message.text):
        await message.answer(_("Incorrect Name"))
        return

    name = get.get_name(message.text)
    report = get.get_current_user_report(message.chat.id)
    report.client.name = name
    await set_state.set_date_state(message, state)


@form_router.message(Form.date, F.text)
async def process_date(message: types.Message, state: FSMContext) -> None:
    if not vld.is_valid_date(message.text):
        await message.answer(_("Incorrect Date"))
        return

    date = get.get_date(message.text)
    report = get.get_current_user_report(message.chat.id)
    report.date = date
    await set_state.set_client_phone_state(message, state)


@form_router.message(Form.client_phone, F.text)
async def process_phone(message: types.Message, state: FSMContext) -> None:
    if not vld.is_valid_phone(message.text):
        await message.answer(_("Incorrect phone"))
        return

    phone = get.get_phone(message.text)
    report = get.get_current_user_report(message.chat.id)
    report.client.phone = phone
    await set_state.set_client_address_state(message, state)


@form_router.message(Form.client_address, F.text)
async def process_address(message: types.Message, state: FSMContext) -> None:
    if not vld.is_valid_address(message.text):
        await message.answer(_("Incorrect address"))
        return

    address = get.get_address(message.text)
    report = get.get_current_user_report(message.chat.id)
    report.client.address = address
    await set_state.set_service_state(message, state)


@form_router.message(Form.add_other_room, F.text)
async def process_address(message: types.Message, state: FSMContext) -> None:
    if not vld.is_valid_address(message.text):
        await message.answer(_("Incorrect room"))
        return
    room_name = message.text.strip() # Получаем текст и убираем пробелы
    # Получаем текущий отчет и комнату
    room = get.get_current_user_room(message.chat.id)

    # Обновляем тип комнаты
    room.room_type = room_name
    room.room_object = room_name  # Можно также сохранить имя комнаты


    report = get.get_current_user_report(message.chat.id)
    
    if report.service == Report.Service.SERVICE:
         await set_state.set_block_state(message,state)

    elif report.service == Report.Service.MAINTENANCE:
        await set_state.set_room_maintenance_nodes_state(message,state)

    elif report.service == Report.Service.CHECK_LIST:
        await set_state.set_check_list_factors_state(message, state)

    else:
        await message.answer(_("Unexpected service type"))



@form_router.message(Form.cleaning_node_await_answer, F.text)
async def process_cleaning_node_add_other(message: types.Message, state: FSMContext):
    room = get.get_current_user_room(message.chat.id)
    if len(message.text) > 31:
        await message.answer(_("Cleaning node name is too long! Should be < 31"))
        return
    room.add_node(CleaningNode(message.text, CleaningNode.Type.OTHER))
    
    report = get.get_current_user_report(message.chat.id)
        # Определение состояния (CLEANING или TEAM)
    if report.service == Report.Service.SERVICE:
        if room.block_type == "INDOOR":    
            await set_state.set_room_indoor_service_nodes_state(message,state)
        elif room.block_type == "OUTDOOR":    
            await set_state.set_room_outdoor_service_nodes_state(message,state)
        elif room.block_type == "OTHER":    
            await set_state.set_room_other_service_nodes_state(message,state)

    elif report.service == Report.Service.MAINTENANCE:
        await set_state.set_room_maintenance_nodes_state(message,state)

    elif report.service == Report.Service.CHECK_LIST:
            room_factors = room.room_factors
            
            if room_factors == "FULL_MAINTENANCE":          
                await set_state.set_check_list_full_maintenancee_nodes_state(message,state)
            elif room_factors == "SUPPORT":          
                await set_state.set_check_list_support_nodes_state(message,state)
            elif room_factors == "OTHER":          
                await set_state.set_check_list_other_nodes_state(message,state)
    else:
        await message.answer(_("Unexpected service type"))


# Обработчик фото ДО
@form_router.message(Form.cleaning_node_img_before, F.photo)
async def process_cleaning_node_img_before(message: types.Message, state: FSMContext):
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    # Получаем текущий узел
    current_node = room.current_node
    if current_node is None:
        await message.answer(_("No active cleaning node"))
        return
    
    # Находим индекс узла
    node_index, node_type = room.find_node_index(current_node.name)
    if node_index == -1:
        await message.answer(_("Node not found"))
        return
    
    # Сохраняем фото ДО через метод Room
    room.update_node_photo_before(
        node_index=node_index,
        photo=message.photo[-1],
        node_type=node_type
    )
    
    # Переходим к следующему узлу
    room.next_cleaning_node()

    if room.nodes_queue_empty():
        room.create_nodes_queue()
        await set_state.set_img_after_state(message, state)
        return

    translated_node = _(room.current_node.button_text)
    await inline.send_skip_keyboard(message, _("Send photo BEFORE for {}").format(translated_node))


# Обработчик фото ПОСЛЕ
@form_router.message(Form.cleaning_node_img_after, F.photo)
async def process_cleaning_node_img_after(message: types.Message, state: FSMContext):
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    # Получаем текущий узел
    current_node = room.current_node
    if current_node is None:
        await message.answer(_("No active cleaning node"))
        return
    
    # Находим индекс узла
    node_index, node_type = room.find_node_index(current_node.name)
    if node_index == -1:
        await message.answer(_("Node not found"))
        return
    
    # Сохраняем фото ПОСЛЕ через метод Room
    room.update_node_photo_after(
        node_index=node_index,
        photo=message.photo[-1],
        node_type=node_type
    )

    # Проверяем тип отчета
    if report.service == Report.Service.SERVICE:
        # Переход в состояние ожидания комментария для каждой ноды
        await state.set_state(Form.cleaning_node_comment)
        await inline.send_skip_keyboard(message, _("Now write a recommendation for the photo"))
    elif report.service == Report.Service.MAINTENANCE:
        # Переход к следующему узлу без запроса комментария для нод
        room.next_cleaning_node()

        if room.nodes_queue_empty():
            room = get.get_current_user_room(message.chat.id)
            if not room.room_comment:
                await state.set_state(Form.cleaning_room_comment)
                await inline.send_skip_keyboard(message, _("Now write a recommendation for the room"))
                
            else:
                await set_state.set_check_report_state(message, state)

        else:
            await state.set_state(Form.cleaning_node_img_after)
            translated_node = _(room.current_node.button_text)
            await inline.send_skip_keyboard(message, _("Send photo AFTER for {}").format(translated_node))


# Обработчик комментария для узла (SERVICE)
@form_router.message(Form.cleaning_node_comment, F.text)
async def process_cleaning_node_comment(message: types.Message, state: FSMContext):
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    if report.service == Report.Service.SERVICE:
        # Получаем текущий узел
        current_node = room.current_node
        if current_node is None:
            await message.answer(_("No active cleaning node"))
            return
        
        if message.text.lower() != "skip":
            # Находим индекс узла
            node_index, node_type = room.find_node_index(current_node.name)
            if node_index == -1:
                await message.answer(_("Node not found"))
                return
            
            # Сохраняем комментарий через метод Room
            room.update_node_comment(
                node_index=node_index,
                comment=message.text,
                node_type=node_type
            )

        # Переход к следующему узлу уборки
        room.next_cleaning_node()

        if room.nodes_queue_empty():
            await set_state.set_check_report_state(message, state)
        else:
            await state.set_state(Form.cleaning_node_img_after)
            translated_node = _(room.current_node.button_text)
            await inline.send_skip_keyboard(message, _("Send photo AFTER for {}").format(translated_node))


# Обработчик комментария для комнаты (MAINTENANCE)
@form_router.message(Form.cleaning_room_comment, F.text)
async def process_cleaning_room_comment(message: types.Message, state: FSMContext):
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    if report.service == Report.Service.MAINTENANCE:
        room.room_comment = message.text
        await set_state.set_check_report_state(message, state)



# /////

# Обработчик фото ДО
@form_router.message(Form.waiting_for_photo_before, F.photo)
async def process_photo_before(
    message: types.Message,
    state: FSMContext
):
    data = await state.get_data()
    report = get.get_current_user_report(message.chat.id)

    # Находим нужную комнату
    # room = next(r for r in report.rooms if r.room_type == data['current_room_type'])
    room= get.get_current_user_room(message.chat.id)
    
    # Находим индекс узла
    node_index, node_type = room.find_node_index(data['current_node_name'])
    
    if node_index == -1:
        await message.answer(_("Node not found"))
        return
    
    # Сохраняем фото ДО
    room.update_node_photo_before(node_index, message.photo[-1], node_type)
    
    if report.service in [Report.Service.SERVICE, Report.Service.MAINTENANCE]:
        await state.set_state(Form.waiting_for_photo_after)
        await inline.send_skip_keyboard(message, _("Photo BEFORE add. Send photo AFTER for") + " " + data['current_node_name'])
    elif report.service == Report.Service.CHECK_LIST:
        await message.answer(_("BEFORE photo added!"))
        await state.clear()
        await set_state.set_check_report_state(message, state)


# Обработчик фото ПОСЛЕ
@form_router.message(Form.waiting_for_photo_after, F.photo)
async def process_photo_after(
    message: types.Message,
    state: FSMContext
):
    data = await state.get_data()
    report = get.get_current_user_report(message.chat.id)
    
    # Находим нужную комнату
    # room = next(r for r in report.rooms if r.room_type == data['current_room_type'])
    room= get.get_current_user_room(message.chat.id)
    
    # Находим индекс узла
    node_index, node_type = room.find_node_index(data['current_node_name'])
    
    if node_index == -1:
        await message.answer(_("Node not found"))
        return
    
    # Сохраняем фото ПОСЛЕ
    room.update_node_photo_after(node_index, message.photo[-1], node_type)
    
    await state.clear()
    await message.answer(_("Photos saved! Node data updated."))
    await set_state.set_check_report_state(message, state)


# Обработчик комментария
@form_router.message(Form.waiting_for_comment, F.text)
async def process_comment(
    message: types.Message,
    state: FSMContext
):
    data = await state.get_data()
    report = get.get_current_user_report(message.chat.id)
    
    # Находим конкретную комнату по типу
    # room = next(r for r in report.rooms if r.room_type == data['current_room_type'])
    room= get.get_current_user_room(message.chat.id)
    
    # Находим индекс узла
    node_index, node_type = room.find_node_index(data['current_node_name'])
    
    if node_index == -1:
        await message.answer(_("Node not found"))
        return
    
    # Сохраняем комментарий
    service_name = report.service.name
    if service_name == "MAINTENANCE":
        room.room_comment = message.text

    elif service_name == "SERVICE":
        room.update_node_comment(node_index, message.text, node_type)

    else:
        room.update_node_comment(node_index, "", node_type)
        room.room_comment = ""
    
    await state.clear()
    await message.answer(_("Comment saved! Node data updated."))
    await set_state.set_check_report_state(message, state)

@form_router.message(Form.waiting_for_video, F.video)
async def process_video(
    message: types.Message,
    state: FSMContext
):
    data = await state.get_data()
    report = get.get_current_user_report(message.chat.id)

    # Получаем video объект
    video = message.video
    video_id = video.file_id
    
    # Проверяем размер видео (20 МБ = 20 * 1024 * 1024 байт)
    MAX_VIDEO_SIZE = 20 * 1024 * 1024  # 20 МБ в байтах
    
    if video.file_size > MAX_VIDEO_SIZE:
        await message.answer(_(
        "The video is too large! The maximum size is 20 MB.\n"
        "Please compress the video and resubmit it."
        ))
        # Остаемся в том же состоянии, ожидая повторной отправки
        return
    
    print(f"Video file_id: {video_id}")
    
    # Находим конкретную комнату по типу
    room = get.get_current_user_room(message.chat.id)
    
    # Находим индекс узла
    node_index, node_type = room.find_node_index(data['current_node_name'])
    
    if node_index == -1:
        await message.answer(_("Node not found"))
        return
    
    # Сохраняем видео
    service_name = report.service.name
    if service_name == "MAINTENANCE":
        room.room_video_id = video_id  # Сохраняем file_id для комнаты

    elif service_name == "SERVICE":
        room.update_node_video(node_index, video, node_type)  # Используем новый метод

    else:
        print("Unknown service type, video not saved")
    
    await state.clear()
    await message.answer(_("Video ID saved! Video will be downloaded when report is generated."))
    await set_state.set_check_report_state(message, state)
# /////


@form_router.message(Form.custom_work_master, F.text)
async def process_custom_master(
    message: types.Message,
    state: FSMContext,
    # bot: Bot
):
    master_name = message.text  
    # Находим конкретную комнату по типу
    room = get.get_current_user_room(message.chat.id)
    room.master = master_name
    
    # await send_pdf_report(bot, message)
    await state.clear()
    await message.answer(_("Room master saved!"))
    await set_state.set_check_report_state(message, state)


from aiogram.filters import Command
from loader import bot  


@form_router.message(Command("report"))
async def handle_report_command(message: types.Message):
    """Обработчик команды для генерации отчета"""
    # Всегда генерируем сначала на английском
    await send_pdf_report(bot, message, locale="en")