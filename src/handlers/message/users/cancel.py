from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from src.models.report import Report
from src.states.form import Form

import src.misc.getters as get
from src.states import setters as set_state
from src.models.cleaningnode import DEFAULT_SERVICE_NODES, DEFAULT_MAINTENANCE_NODES

from loader import users

router = Router()


@router.message(Form.client_name, Command(commands=["cancel"]))
async def cancel_client_name(message: types.Message, state: FSMContext) -> None:
    await set_state.set_client_name_state(message, state)


@router.message(Form.date, Command(commands=["cancel"]))
async def cancel_date(message: types.Message, state: FSMContext) -> None:
    await set_state.set_client_name_state(message, state)


@router.message(Form.client_phone, Command(commands=["cancel"]))
async def cancel_client_phone(message: types.Message, state: FSMContext) -> None:
    await set_state.set_date_state(message, state)


@router.message(Form.client_address, Command(commands=["cancel"]))
async def cancel_client_address(message: types.Message, state: FSMContext) -> None:
    await set_state.set_client_phone_state(message, state)


@router.message(Form.service, Command(commands=["cancel"]))
async def cancel_service(message: types.Message, state: FSMContext) -> None:
    # Восстанавливаем оригинальную логику из старого кода
    await set_state.set_client_address_state(message, state)


@router.message(Form.add_other_room, Command(commands=["cancel"]))
async def cancel_add_other_room(message: types.Message, state: FSMContext) -> None:
    await set_state.set_room_state(message, state)


@router.message(Form.add_block, Command(commands=["cancel"]))
async def cancel_block_factors(message: types.Message, state: FSMContext) -> None:
    await set_state.set_room_state(message, state)


@router.message(Form.add_other_block, Command(commands=["cancel"]))
async def cancel_add_other_block(message: types.Message, state: FSMContext) -> None:
    await set_state.set_block_state(message, state)


@router.message(Form.check_list_factors, Command(commands=["cancel"]))
async def cancel_check_list_factors(message: types.Message, state: FSMContext) -> None:
    await set_state.set_room_state(message, state)


@router.message(Form.add_check_list_factors, Command(commands=["cancel"]))
async def cancel_add_check_list_factors(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_list_factors_state(message, state)


@router.message(Form.add_room, Command(commands=["cancel"]))
async def cancel_add_room(message: types.Message, state: FSMContext) -> None:
    report = get.get_current_user_report(message.chat.id)
    room = get.get_current_user_room(message.chat.id)
    
    if len(report.rooms) > 1:
        # Удаляем текущую комнату и возвращаемся к предыдущей
        report.rooms.pop()
        # await set_state.set_add_room_state(message, state)
        # await state.set_state(Form.check_report)
        await set_state.set_check_report_state(message, state)
        return
    
    # Если это первая комната, возвращаемся к выбору услуги
    room.clear_all_cleaning_nodes()
    await set_state.set_service_state(message, state)


@router.message(Form.room_cleaning_nodes, Command(commands=["cancel"]))
async def cancel_room_cleaning_nodes(message: types.Message, state: FSMContext) -> None:
    report = get.get_current_user_report(message.chat.id)
    
    if report.service == Report.Service.CHECK_LIST:
        await set_state.set_check_list_factors_state(message, state)
        return
    
    room = get.get_current_user_room(message.chat.id)
    room.clear_all_cleaning_nodes()
    
    if report.service == Report.Service.SERVICE:
        await set_state.set_block_state(message, state)
    else:
        await set_state.set_room_state(message, state)


@router.message(Form.room_check_list_nodes, Command(commands=["cancel"]))
async def cancel_working_factors(message: types.Message, state: FSMContext):
    report = get.get_current_user_report(message.chat.id)
    room = get.get_current_user_room(message.chat.id)
    
    room.clear_all_cleaning_nodes()
    await set_state.set_check_list_factors_state(message, state)


@router.message(Form.cleaning_node_await_answer, Command(commands=["cancel"]))
async def cancel_cleaning_node_answer(message: types.Message, state: FSMContext):
    report = get.get_current_user_report(message.chat.id)
    room = get.get_current_user_room(message.chat.id)
    
    if report.service == Report.Service.CHECK_LIST:
        room_factors = room.room_factors
        if room_factors == "FULL_MAINTENANCE":
            await set_state.set_check_list_full_maintenancee_nodes_state(message, state)
        elif room_factors == "SUPPORT":
            await set_state.set_check_list_support_nodes_state(message, state)
        elif room_factors == "OTHER":
            await set_state.set_check_list_other_nodes_state(message, state)
    elif report.service == Report.Service.SERVICE:
        if room.block_type == "INDOOR":
            await set_state.set_room_indoor_service_nodes_state(message, state)
        elif room.block_type == "OUTDOOR":
            await set_state.set_room_outdoor_service_nodes_state(message, state)
        elif room.block_type == "OTHER":
            await set_state.set_room_other_service_nodes_state(message, state)
    elif report.service == Report.Service.MAINTENANCE:
        await set_state.set_room_maintenance_nodes_state(message, state)


@router.message(Form.cleaning_node_img_before, Command(commands=["cancel"]))
async def cancel_img_before(message: types.Message, state: FSMContext) -> None:
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    if room._index == 0:
        if report.service == Report.Service.SERVICE:
            # Определяем какой тип блоков был выбран
            if room.block_type == "INDOOR":
                await set_state.set_room_indoor_service_nodes_state(message, state)
            elif room.block_type == "OUTDOOR":
                await set_state.set_room_outdoor_service_nodes_state(message, state)
            elif room.block_type == "OTHER":
                await set_state.set_room_other_service_nodes_state(message, state)
            else:
                await set_state.set_room_service_nodes_state(message, state)
        elif report.service == Report.Service.MAINTENANCE:
            await set_state.set_room_maintenance_nodes_state(message, state)
        elif report.service == Report.Service.CHECK_LIST:
            room_factors = room.room_factors
            if room_factors == "FULL_MAINTENANCE":
                await set_state.set_check_list_full_maintenancee_nodes_state(message, state)
            elif room_factors == "SUPPORT":
                await set_state.set_check_list_support_nodes_state(message, state)
            elif room_factors == "OTHER":
                await set_state.set_check_list_other_nodes_state(message, state)
    else:
        room.nodes_queue_back()
        await set_state.set_img_before_state(message, state)


@router.message(Form.cleaning_node_img_after, Command(commands=["cancel"]))
async def cancel_img_after(message: types.Message, state: FSMContext) -> None:
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    if room._index == 0:
        # Сбрасываем очередь и возвращаемся к выбору фото "до"
        room.create_nodes_queue()
        if room.current_node:
            await set_state.set_img_before_state(message, state)
        else:
            # Если нет текущего узла, возвращаемся к выбору узлов
            if report.service == Report.Service.SERVICE:
                if room.block_type == "INDOOR":
                    await set_state.set_room_indoor_service_nodes_state(message, state)
                elif room.block_type == "OUTDOOR":
                    await set_state.set_room_outdoor_service_nodes_state(message, state)
                elif room.block_type == "OTHER":
                    await set_state.set_room_other_service_nodes_state(message, state)
                else:
                    await set_state.set_room_service_nodes_state(message, state)
            elif report.service == Report.Service.MAINTENANCE:
                await set_state.set_room_maintenance_nodes_state(message, state)
    else:
        room.nodes_queue_back()
        if room.current_node:
            await set_state.set_img_after_state(message, state)



@router.message(Form.cleaning_room_comment, Command(commands=["cancel"]))
async def cancel_cleaning_room_comment(message: types.Message, state: FSMContext) -> None:
    """
    Отмена ввода комментария комнаты - возврат к добавлению фото ПОСЛЕ
    для того же узла, который был до перехода к комментарию
    """
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    if report.service != Report.Service.MAINTENANCE:
        await set_state.set_check_report_state(message, state)
        return
    
    # Очищаем комментарий комнаты
    room.room_comment = None
    
    # ВОССТАНАВЛИВАЕМ очередь узлов в том же состоянии, как было до перехода к комментарию
    # Предполагаем, что при переходе к комментарию очередь уже была создана
    # и мы находимся на последнем узле
    
    if room.nodes_queue_empty():
        # Если очередь пуста, создаем ее заново
        room.create_nodes_queue()
    
    if room.nodes_queue_empty():
        # Если все еще нет узлов
        await set_state.set_check_report_state(message, state)
        return
    
    # Устанавливаем индекс на ПРЕДЫДУЩИЙ узел (тот, для которого мы должны были добавить фото ПОСЛЕ)
    # По логике, при переходе к комментарию комнаты мы уже прошли все узлы
    # Так что возвращаемся к ПОСЛЕДНЕМУ узлу в очереди
    
    room._index = len(room.nodes_queue) - 1  # Последний узел
    
    # Альтернативно, можно использовать существующий индекс если он не сброшен
    # if room._index >= len(room.nodes_queue):
    #     room._index = len(room.nodes_queue) - 1
    
    if room.current_node:
        await set_state.set_img_after_state(message, state)
    else:
        await set_state.set_check_report_state(message, state)

@router.message(Form.cleaning_room_comment, Command(commands=["cancel"]))
async def cancel_cleaning_room_comment(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.check_report, Command(commands=["cancel"]))
async def cancel_check_report(message: types.Message, state: FSMContext) -> None:
    room = get.get_current_user_room(message.chat.id)
    report = get.get_current_user_report(message.chat.id)
    
    # Сохраняем важные параметры перед очисткой
    service_type = report.service
    block_type = getattr(room, 'block_type', None)
    room_factors = getattr(room, 'room_factors', None)
    room_type = getattr(room, 'room_type', None)
    room_object = getattr(room, 'room_object', None)
    
    # Всегда очищаем данные последней комнаты
    # Если у нас есть метод clear_room_data, используем его
    if hasattr(room, 'clear_room_data'):
        room.clear_room_data()
    else:
        # Альтернатива: очищаем все вручную
        room.clear_all_cleaning_nodes()
        room.room_comment = None
        room.room_video_id = None
        room.master = None
    
    # Восстанавливаем важные параметры после очистки
    if room_type:
        room.room_type = room_type
    if room_object:
        room.room_object = room_object
    if block_type:
        room.block_type = block_type
    if room_factors:
        room.room_factors = room_factors
    
    # Возвращаемся к редактированию узлов в зависимости от типа сервиса
    if service_type == Report.Service.SERVICE:
        if block_type == "INDOOR":
            await set_state.set_room_indoor_service_nodes_state(message, state)
        elif block_type == "OUTDOOR":
            await set_state.set_room_outdoor_service_nodes_state(message, state)
        elif block_type == "OTHER":
            await set_state.set_room_other_service_nodes_state(message, state)
        else:
            # Если блок не выбран, возвращаемся к выбору блока
            await set_state.set_block_state(message, state)
            
    elif service_type == Report.Service.MAINTENANCE:
        await set_state.set_room_maintenance_nodes_state(message, state)
        
    elif service_type == Report.Service.CHECK_LIST:
        if room_factors == "FULL_MAINTENANCE":
            await set_state.set_check_list_full_maintenancee_nodes_state(message, state)
        elif room_factors == "SUPPORT":
            await set_state.set_check_list_support_nodes_state(message, state)
        elif room_factors == "OTHER":
            await set_state.set_check_list_other_nodes_state(message, state)
        else:
            # Если факторы не выбраны, возвращаемся к выбору факторов
            await set_state.set_check_list_factors_state(message, state)
    else:
        # Если тип сервиса неизвестен, возвращаемся к выбору сервиса
        await set_state.set_service_state(message, state)

        
@router.message(Form.waiting_work_master, Command(commands=["cancel"]))
async def cancel_waiting_master(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.custom_work_master, Command(commands=["cancel"]))
async def cancel_custom_master(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.check_report_add_data, Command(commands=["cancel"]))
async def cancel_check_report_add_data(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.waiting_for_comment, Command(commands=["cancel"]))
async def cancel_waiting_for_comment(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.waiting_for_photo_before, Command(commands=["cancel"]))
async def cancel_waiting_for_photo_before(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.waiting_for_photo_after, Command(commands=["cancel"]))
async def cancel_waiting_for_photo_after(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


@router.message(Form.waiting_for_video, Command(commands=["cancel"]))
async def cancel_waiting_for_video(message: types.Message, state: FSMContext) -> None:
    await set_state.set_check_report_state(message, state)


# Общий обработчик для всех остальных состояний
@router.message(Command(commands=["cancel"]))
async def cancel_any_state(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(_("Nothing to cancel. Start with /start"))
        return
    
    # Для состояний, которые не имеют обработчика, очищаем все
    users.pop(message.chat.id, None)
    await state.clear()
    
    await message.answer(_(
        "Operation cancelled. All data has been cleared.\n"
        "Start a new report with /start"
    ))