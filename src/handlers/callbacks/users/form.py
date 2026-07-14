from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.filters import StateFilter

from datetime import datetime, timedelta

import src.keyboards.inline as inline
from src.states import Form
from src.states import setters as set_state

import src.misc.getters as get

from src.models import Report, CleaningNode, Room,Block,Time

from src.services.pdfreport import pdfGenerator


from src.callbackdata import (
    OtherExtraServiceCB,
    ServiceCB,
    ExtraServiceCB,
    ClientCB,
    CleaningNodeCB,
    FactorCB,
    RoomTypeCB,
    BlockTypeCB,
    TimeTypeCB,
    NodeActionCB,
    IncompleteNodeCB,
    CheckListNodeCB,
    MasterCB
)
from src.misc.utils import slugify

from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.callback_query(TimeTypeCB.filter(F.type.in_([Time.Type.EREYESTERDEY, Time.Type.YESTERDAY, Time.Type.TODAY])))
async def process_time_type_selection(callback: types.CallbackQuery, callback_data: TimeTypeCB, state: FSMContext):
    try:
        await callback.answer()
        
        # Получаем текущую дату
        today = datetime.now().date()
        
        # Устанавливаем дату в зависимости от выбранного типа
        if callback_data.type == Time.Type.TODAY:
            selected_date = today
        elif callback_data.type == Time.Type.YESTERDAY:
            selected_date = today - timedelta(days=1)
        elif callback_data.type == Time.Type.EREYESTERDEY:
            selected_date = today - timedelta(days=2)
        else:
            selected_date = today
        
        # Сохраняем дату в отчет
        report = get.get_current_user_report(callback.message.chat.id)
        report.date = selected_date

        # Переходим к следующему состоянию
        await set_state.set_client_phone_state(callback.message, state)
        
    except Exception as e:
        print(f"[ERROR] In process_time_type_selection: {str(e)}")
        await callback.message.answer(_("An error occurred. Please try again."))

@router.callback_query(Form.client_type, ClientCB.filter())
async def callback_client_type(
    callback: types.CallbackQuery,
    callback_data: ClientCB,
    state: FSMContext,
):
    await callback.answer()
    report = get.get_current_user_report(callback.message.chat.id)
    report.client.type = callback_data.type

    await state.set_state(Form.client_address)
    await callback.message.answer(_("Enter client address:"))



@router.callback_query(
    Form.service, ServiceCB.filter(F.service.in_([Report.Service.SERVICE, Report.Service.MAINTENANCE,Report.Service.CHECK_LIST]))
)
async def callback_service_team(
    callback: types.CallbackQuery, state: FSMContext, callback_data: ServiceCB
):
    await callback.answer()

    report = get.get_current_user_report(callback.message.chat.id)
    report.service = callback_data.service
    # await state.set_state(Form.add_room)

    await set_state.set_room_state(callback.message, state)




# add room
@router.callback_query(
    Form.add_room, RoomTypeCB.filter()
    )

async def callback_extra_service(
    callback: types.CallbackQuery, callback_data: RoomTypeCB, state: FSMContext):
    room_type = callback_data.type

    room = get.get_current_user_room(callback.message.chat.id)
    room.room_type = room_type.name
    room.room_object = room_type
    
    report = get.get_current_user_report(callback.message.chat.id)
    if room_type == "Unknown":

        await state.set_state(Form.add_other_room)
        await callback.message.answer(_("Enter room"))

    else:
        if report.service == Report.Service.SERVICE:
            await set_state.set_block_state(callback.message,state)
            # await set_state.set_room_service_nodes_state(callback.message,state)
        elif report.service == Report.Service.MAINTENANCE:
            
            await set_state.set_room_maintenance_nodes_state(callback.message,state)
        elif report.service == Report.Service.CHECK_LIST:
            await set_state.set_check_list_factors_state(callback.message,state)

        else:
            await callback.message.answer(_("Unexpected service type"))
        
    await callback.answer()



@router.callback_query(
    Form.add_block, BlockTypeCB.filter()
    )

async def callback_block_service(
    callback: types.CallbackQuery, callback_data: BlockTypeCB, state: FSMContext):
    block_type = callback_data.type.name

    
    report = get.get_current_user_report(callback.message.chat.id)
    if block_type == "UNKNOWN":

        await state.set_state(Form.add_other_block)
        await callback.message.answer(_("Enter block"))

    else:
        if report.service == Report.Service.SERVICE:
            # await set_state.set_block_state(callback.message,state)\
            room = get.get_current_user_room(callback.message.chat.id)
            room.block_type = block_type

            if block_type == "INDOOR":          
                await set_state.set_room_indoor_service_nodes_state(callback.message,state)
            elif block_type == "OUTDOOR":          
                await set_state.set_room_outdoor_service_nodes_state(callback.message,state)
            elif block_type == "OTHER":          
                await set_state.set_room_other_service_nodes_state(callback.message,state)
        else:
            await callback.message.answer(_("Unexpected service type"))
        
    await callback.answer()




@router.callback_query(
    Form.check_list_factors, FactorCB.filter()
    )

async def callback_add_work_factor(
    callback: types.CallbackQuery, callback_data: FactorCB, state: FSMContext):
    room_factors = callback_data.type.name
    report = get.get_current_user_report(callback.message.chat.id)
    if room_factors == "UNKNOWN":

        await state.set_state(Form.add_check_list_factors)
        await callback.message.answer(_("Enter work factors"))

    else:
        if report.service == Report.Service.CHECK_LIST:
            room = get.get_current_user_room(callback.message.chat.id)
            room.room_factors = room_factors
            
            if room_factors == "FULL_MAINTENANCE":          
                await set_state.set_check_list_full_maintenancee_nodes_state(callback.message,state)
            elif room_factors == "SUPPORT":          
                await set_state.set_check_list_support_nodes_state(callback.message,state)
            elif room_factors == "OTHER":          
                await set_state.set_check_list_other_nodes_state(callback.message,state)
        else:
            await callback.message.answer(_("Unexpected service type"))
        
    await callback.answer()



@router.callback_query(
    Form.room_cleaning_nodes, 
    CleaningNodeCB.filter(F.action == "page")
)
async def callback_change_page_cleaning_node(
    callback: types.CallbackQuery, 
    callback_data: CleaningNodeCB,
    state: FSMContext
):
    # Получаем номер страницы из callback_data
    
    page = callback_data.page
    await callback.answer()
    report = get.get_current_user_report(callback.message.chat.id)

    if report.service == Report.Service.MAINTENANCE:
        await inline.edit_maintenance_node_keyboard(
            callback.message, 
            page=page
        )
    elif report.service == Report.Service.SERVICE:
        room = get.get_current_user_room(callback.message.chat.id)
        if room.block_type == "INDOOR":
            await inline.edit_service_indoor_node_keyboard(callback.message)
        elif room.block_type == "OUTDOOR":
            await inline.edit_service_outdoor_node_keyboard(callback.message)
        elif room.block_type == "OTHER":
            await inline.edit_service_other_node_keyboard(callback.message)
    


@router.callback_query(
    Form.room_cleaning_nodes, CleaningNodeCB.filter(F.action == "add")
)
async def callback_add_cleaning_node(
    callback: types.CallbackQuery, callback_data: CleaningNodeCB
):
    await callback.answer()
    room = get.get_current_user_room(callback.message.chat.id)
    # Добавляем узел с учетом страницы
    room.add_default_node(callback_data.index)
    report = get.get_current_user_report(callback.message.chat.id)

    if report.service == Report.Service.SERVICE:

        if room.block_type == "INDOOR":    
            await inline.edit_service_indoor_node_keyboard(callback.message)
        elif room.block_type == "OUTDOOR":    
            await inline.edit_service_outdoor_node_keyboard(callback.message)
        elif room.block_type == "OTHER":    
            await inline.edit_service_other_node_keyboard(callback.message)
    elif report.service == Report.Service.MAINTENANCE:
        await inline.edit_maintenance_node_keyboard(
            callback.message, 
            page=callback_data.page  # Сохраняем текущую страницу
        )
    else:
        await callback.answer(_("An error occurred while adding the node"), show_alert=True)


@router.callback_query(
    Form.room_cleaning_nodes, CleaningNodeCB.filter(F.action == "delete")
)
async def callback_delete_cleaning_node(
    callback: types.CallbackQuery, callback_data: CleaningNodeCB
):
    await callback.answer()
    room = get.get_current_user_room(callback.message.chat.id)
    # Передаем номер страницы в delete_node
    room.delete_node(callback_data.index,callback_data.type)

    # Обновляем клавиатуру
    report = get.get_current_user_report(callback.message.chat.id)
    if report.service == Report.Service.MAINTENANCE:
        await inline.edit_maintenance_node_keyboard(
            callback.message, 
            page=callback_data.page  # Сохраняем текущую страницу
        )
    elif report.service == Report.Service.SERVICE:
        if room.block_type == "INDOOR":    
            await inline.edit_service_indoor_node_keyboard(callback.message)
        elif room.block_type == "OUTDOOR":    
            await inline.edit_service_outdoor_node_keyboard(callback.message)
        elif room.block_type == "OTHER":    
            await inline.edit_service_other_node_keyboard(callback.message)
    else:
        print(f"[WARNING] [DELETE_NODE] Unknown service type: {report.service}")


@router.callback_query(
    Form.room_cleaning_nodes, CleaningNodeCB.filter(F.action == "add_other")
)
async def callback_add_other_cleaning_node(
    callback: types.CallbackQuery, state: FSMContext
):
    await callback.answer()
    await state.set_state(Form.cleaning_node_await_answer)
    await callback.message.answer(_("Please type other cleaning node"))

@router.callback_query(
    Form.room_cleaning_nodes, CleaningNodeCB.filter(F.action == "enter")
)
async def callback_enter_cleaning_node(
    callback: types.CallbackQuery, state: FSMContext
):
    room = get.get_current_user_room(callback.message.chat.id)
    
    # Проверяем, выбрана ли хотя бы одна нода
    has_selected = any(active for _, active in room.default_cleaning_nodes)
    if not has_selected and not room.cleaning_nodes:
        await callback.answer(
            _("Please select at least one node before continuing"),
            show_alert=True
        )
        return
    
    await callback.answer()
    report = get.get_current_user_report(callback.message.chat.id)
    if report.service == Report.Service.MAINTENANCE:
        # FOR TURN COMMENTS ADN PHOTOS
        await start_getting_photos(callback.message, state)

    else:
        # FOR SKIP COMMENTS ADN PHOTOS
        # await set_state.set_add_room_state(callback.message, state)
        await set_state.set_check_report_state(callback.message, state)



@router.callback_query(
    Form.room_check_list_nodes,
    CheckListNodeCB.filter(F.action == "immte")
)
async def callback_set_immediate(
    callback: types.CallbackQuery,
    callback_data: CheckListNodeCB,
    state: FSMContext
):
    await callback.answer()
    node_name = callback_data.node_name
    room = get.get_current_user_room(callback.message.chat.id)

    if not room:
        await callback.answer(_("Room not found"), show_alert=True)
        return

    node_index, node_type = room.find_node_index(node_name)
    
    if node_index == -1:
        await callback.answer(_("Node not found"), show_alert=True)
        return

    room.update_node_extra_factors(node_index, "immediate", node_type)
    room_factors = room.room_factors
    if room_factors == "FULL_MAINTENANCE":          
        await inline.edit_check_list_full_maintenance_node_keyboard(callback.message)
    elif room_factors == "SUPPORT":          
        await inline.edit_check_list_support_node_keyboard(callback.message)
    elif room_factors == "OTHER":          
        await inline.edit_check_list_other_node_keyboard(callback.message)



@router.callback_query(
    Form.room_check_list_nodes,
    CheckListNodeCB.filter(F.action == "normal")
)
async def callback_set_normal(
    callback: types.CallbackQuery,
    callback_data: CheckListNodeCB,
    state: FSMContext
):
    await callback.answer()
    node_name = callback_data.node_name
    room = get.get_current_user_room(callback.message.chat.id)

    if not room:
        await callback.answer(_("Room not found"), show_alert=True)
        return

    node_index, node_type = room.find_node_index(node_name)
    
    if node_index == -1:
        await callback.answer(_("Node not found"), show_alert=True)
        return

    room.update_node_extra_factors(node_index, "normal", node_type)
    room.set_node_status(node_index, True, node_type)  # Активируем узел
 
    room_factors = room.room_factors
    if room_factors == "FULL_MAINTENANCE":          
        await inline.edit_check_list_full_maintenance_node_keyboard(callback.message)
    elif room_factors == "SUPPORT":          
        await inline.edit_check_list_support_node_keyboard(callback.message)
    elif room_factors == "OTHER":          
        await inline.edit_check_list_other_node_keyboard(callback.message)



@router.callback_query(
    Form.room_check_list_nodes,
    CheckListNodeCB.filter(F.action == "delete")
)
async def callback_delete_node(
    callback: types.CallbackQuery,
    callback_data: CheckListNodeCB,
    state: FSMContext
):
    await callback.answer()
    node_name = callback_data.node_name
    room = get.get_current_user_room(callback.message.chat.id)

    if not room:
        await callback.answer(_("Room not found"), show_alert=True)
        return

    node_index, node_type = room.find_node_index(node_name)
    
    if node_index == -1:
        await callback.answer(_("Node not found"), show_alert=True)
        return

    if node_type == CleaningNode.Type.DEFAULT:
        # Для дефолтных узлов сбрасываем факторы и деактивируем
        room.update_node_extra_factors(node_index, None, node_type)
        room.set_node_status(node_index, False, node_type)
    elif node_type == CleaningNode.Type.OTHER:
        # Для кастомных узлов удаляем полностью
        room.delete_node(node_index, node_type)

    room_factors = room.room_factors
    if room_factors == "FULL_MAINTENANCE":          
        await inline.edit_check_list_full_maintenance_node_keyboard(callback.message)
    elif room_factors == "SUPPORT":          
        await inline.edit_check_list_support_node_keyboard(callback.message)
    elif room_factors == "OTHER":          
        await inline.edit_check_list_other_node_keyboard(callback.message)


@router.callback_query(
    Form.room_check_list_nodes, CleaningNodeCB.filter(F.action == "add_other")
)
async def callback_add_other_cleaning_node(
    callback: types.CallbackQuery, state: FSMContext
):
    await callback.answer()
    await state.set_state(Form.cleaning_node_await_answer)
    await callback.message.answer(_("Please type other cleaning node"))


@router.callback_query(
    Form.room_check_list_nodes, CleaningNodeCB.filter(F.action == "enter")
)
async def callback_enter_check_list_node(
    callback: types.CallbackQuery, state: FSMContext
):
    room = get.get_current_user_room(callback.message.chat.id)
    
    # Проверяем, выбрана ли хотя бы одна нода (с immediate или normal)
    has_selected = any(active for _, active in room.default_cleaning_nodes)
    if not has_selected and not room.cleaning_nodes:
        await callback.answer(
            _("Please select at least one node before continuing"),
            show_alert=True
        )
        return
    
    await callback.answer()

    # await set_state.set_add_room_state(callback.message, state)
    await set_state.set_check_report_state(callback.message, state)


    

async def start_getting_photos(message: types.Message, state: FSMContext):
    room = get.get_current_user_room(message.chat.id)
    room.create_nodes_queue()
    if room.nodes_queue_empty() and room.current_node == None:
        await message.answer(_("You didn't selected cleaning nodes"))
        return

    await set_state.set_img_before_state(message, state)


# Обработчик для кнопки "Пропустить" фото ДО
@router.callback_query(Form.cleaning_node_img_before, F.data == "skip")
async def skip_photo_before(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        room = get.get_current_user_room(callback.message.chat.id)
        
        # Переходим к следующему узлу без сохранения фото
        room.next_cleaning_node()

        if room.nodes_queue_empty():
            room.create_nodes_queue()
            await set_state.set_img_after_state(callback.message, state)
            return

        translated_node = _(room.current_node.button_text)
        await inline.send_skip_keyboard(callback.message, _("Send photo BEFORE for {}").format(translated_node))
        
    except Exception as e:
        await callback.message.answer(_("An error occurred. Please try again."))


# Обработчик для кнопки "Пропустить" фото ПОСЛЕ
@router.callback_query(Form.cleaning_node_img_after, F.data == "skip")
async def skip_photo_after(callback: types.CallbackQuery, state: FSMContext):
    room = get.get_current_user_room(callback.message.chat.id)
    report = get.get_current_user_report(callback.message.chat.id)
    
    # Проверяем тип отчета
    if report.service == Report.Service.SERVICE:
        # Переход в состояние ожидания комментария для каждой ноды
        await state.set_state(Form.cleaning_node_comment)
        await inline.send_skip_keyboard(callback.message, _("Now write a recommendation for the photo"))
    elif report.service == Report.Service.MAINTENANCE:
        # Переход к следующему узлу без запроса комментария для нод
        room.next_cleaning_node()

        if room.nodes_queue_empty():
            room = get.get_current_user_room(callback.message.chat.id)
            if not room.room_comment:
                await state.set_state(Form.cleaning_room_comment)
                await inline.send_skip_keyboard(callback.message, _("Now write a recommendation for the room"))
            else:
                await set_state.set_check_report_state(callback.message, state)
        else:
            await state.set_state(Form.cleaning_node_img_after)
            translated_node = _(room.current_node.button_text)
            await inline.send_skip_keyboard(callback.message, _("Send photo AFTER for {}").format(translated_node))
    
    await callback.answer()

async def check_skip_conditions(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    return (current_state in [Form.cleaning_node_comment, Form.cleaning_room_comment] 
            and callback.data == "skip")

# Обработчик для кнопки "Пропустить" комментария
@router.callback_query(check_skip_conditions)
async def skip_comment(callback: types.CallbackQuery, state: FSMContext):
    room = get.get_current_user_room(callback.message.chat.id)
    report = get.get_current_user_report(callback.message.chat.id)

    if report.service == Report.Service.SERVICE:
        # Просто переходим к следующему узлу без комментария
        room.next_cleaning_node()

        if room.nodes_queue_empty():
            await set_state.set_check_report_state(callback.message, state)
        else:
            await state.set_state(Form.cleaning_node_img_after)
            translated_node = _(room.current_node.button_text)
            await inline.send_skip_keyboard(callback.message, _("Send photo AFTER for {}").format(translated_node))

    elif report.service == Report.Service.MAINTENANCE:
        await set_state.set_check_report_state(callback.message, state)
    
    await callback.answer()

@router.callback_query(Form.check_report, F.data == "yes")
async def callback_add_room_yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    report = get.get_current_user_report(callback.message.chat.id)
    report.add_room() 
    await set_state.set_room_state(callback.message, state)


@router.callback_query(Form.check_report, F.data == "no")
async def callback_add_room_yes(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    await callback.answer()
    # await state.clear()
    # await set_state.set_check_report_state(callback.message, state)
    await send_pdf_report(bot, callback.message)




@router.callback_query(Form.check_report,F.data == "add_master")
async def handle_pdf(    
    callback: types.CallbackQuery, state: FSMContext
):
    await callback.answer()
    await state.set_state(Form.waiting_work_master)
    await inline.send_master_keyboard(callback.message)


# ///////////////

@router.callback_query(Form.check_report, IncompleteNodeCB.filter())
async def handle_incomplete_node(
    callback: types.CallbackQuery, 
    callback_data: IncompleteNodeCB,
    state: FSMContext
):
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    missing_types = set(callback_data.missing_type.split('_'))
    
    # Add appropriate buttons based on missing data types
    if 'p' in missing_types:
        builder.button(
            text=_("Add a photo 📷"),
            callback_data=NodeActionCB(
                action="add_p",
                # room_type=callback_data.room_type,
                node_name=callback_data.node_name,

            )
        )
    
    if 'v' in missing_types:
        builder.button(
            text=_("Add video 📹"),
            callback_data=NodeActionCB(
                action="add_v",
                # room_type=callback_data.room_type,
                node_name=callback_data.node_name
            )
        )
    
    if 'c' in missing_types:
        builder.button(
            text=_("Add a comment 💬"),
            callback_data=NodeActionCB(
                action="add_c",
                # room_type=callback_data.room_type,
                node_name=callback_data.node_name
            )
        )

    # Add Skip button
    builder.button(
        text=_("Skip"),
        callback_data=NodeActionCB(
            action="skip",
            # room_type=callback_data.room_type,
            node_name=callback_data.node_name
        )
    )

    room = get.get_current_user_room(callback.message.chat.id)
    translated_node = _(callback_data.node_name)

    if builder.buttons:
        builder.adjust(1)  # All buttons in one column

        await state.set_state(Form.check_report_add_data)
        await callback.message.edit_text(
            _("Node selected: {}\nWhat would you like to add?").format(translated_node)
            ,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(
            _("Node selected: {}\nNothing to add (no missing data)").format(translated_node)
        )



# Вместо нескольких разных обработчиков используем один с полем action
@router.callback_query(Form.check_report_add_data, NodeActionCB.filter())
async def handle_check_report_node_action(
    callback: types.CallbackQuery,
    callback_data: NodeActionCB,
    state: FSMContext
):
    await callback.answer()
    room = get.get_current_user_room(callback.message.chat.id)
    translated_node = _(callback_data.node_name)

    
    if callback_data.action == "add_c":
        # Сохраняем необходимые данные из callback_data NodeActionCB
        await state.update_data({
            # 'current_room_type': callback_data.room_type,
            'current_node_name': callback_data.node_name
        })
        await state.set_state(Form.waiting_for_comment)
        await inline.send_skip_keyboard(callback.message, _("Please enter a comment:"))
    
    elif callback_data.action == "add_p":
        # Сохраняем необходимые данные из callback_data NodeActionCB
        await state.update_data({
            # 'current_room_type': callback_data.room_type,
            'current_node_name': callback_data.node_name
        })
        await state.set_state(Form.waiting_for_photo_before)
        await inline.send_skip_keyboard(callback.message, _("Send photo BEFORE for {}").format(translated_node))

        
    
    elif callback_data.action == "add_v":
        # Сохраняем необходимые данные из callback_data NodeActionCB
        await state.update_data({
            # 'current_room_type': callback_data.room_type,
            'current_node_name': callback_data.node_name
        })
        await state.set_state(Form.waiting_for_video)
        await inline.send_skip_keyboard(callback.message, _("Please send video\n The maximum size is 20 MB:"))

    
    elif callback_data.action == "skip":
        # Пропускаем действие и возвращаемся к отчету
        await state.clear()
        await set_state.set_check_report_state(callback.message, state)



@router.callback_query(Form.waiting_work_master)
async def process_custom_master(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    # data = await state.get_data()
    if callback.data != "other" and callback.data != "skip":

        # Парсим callback data
        callback_data = MasterCB.unpack(callback.data)
        master_name = callback_data.name

        # report = get.get_current_user_report(callback.message.chat.id)

        # Находим конкретную комнату по типу
        # room = next(r for r in report.rooms if r.room_type == data['current_room_type'])
        room = get.get_current_user_room(callback.message.chat.id)

        room.master = master_name
        
        await state.clear()
        await set_state.set_check_report_state(callback.message, state)


    elif callback.data == "other":
            
        await state.set_state(Form.custom_work_master)
        await inline.send_skip_keyboard(callback.message, _("Send master name"))


    elif callback.data == "skip":
        await callback.answer()  # Обязательно ответить на callback
        await set_state.set_check_report_state(callback.message, state)



# //////////////

@router.callback_query(
    StateFilter(
        Form.waiting_for_comment,
        Form.waiting_for_photo_before,
        Form.waiting_for_photo_after, 
        Form.waiting_for_video,
        Form.custom_work_master

    ),
    F.data == "skip"
)
async def process_skip_check_report(
    callback: types.CallbackQuery,  # Изменено на CallbackQuery
    state: FSMContext
):
    await callback.answer()  # Обязательно ответить на callback
    await set_state.set_check_report_state(callback.message, state)



from loader import i18n_en, i18n_ru  # Импортируем из loader.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def send_pdf_report(bot: Bot, message: types.Message, locale: str = "en"):
    """Генерация PDF на указанном языке"""
    await message.answer(_("Generating..."))  # Сообщение на языке пользователя
    
    # Исправленная строка - передаем chat_id как позиционный аргумент
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_document")
    
    # Генерируем PDF на указанном языке
    pdf_report_path = await generate_report(bot, message.chat.id, locale)
    
    # Подпись на языке пользователя
    caption = _("Thank you for your work!")
    await message.answer_document(
        types.FSInputFile(pdf_report_path), caption=caption
    )
    
    # Добавляем кнопку смены языка если PDF на английском
    if locale == "en":
        await add_language_switch_button(message)

async def add_language_switch_button(message: types.Message):
    """Добавляем кнопку для генерации PDF на русском"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 На RU", callback_data="regenerate_pdf_ru")]
    ])
    await message.answer(_("Need report in Russian?"), reply_markup=keyboard)

from loader import i18n_en, i18n_ru

async def generate_report(bot: Bot, chat_id: int, locale: str) -> str:
    report = get.get_current_user_report(chat_id)
    client_name = slugify(report.client.name, allow_unicode=True)
    report_name = f"MAINTENANCE_REPORT_{client_name}_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}"
    
    # Выбираем функцию перевода в зависимости от языка
    if locale == "ru":
        gettext_func = i18n_ru.gettext
    else:
        gettext_func = i18n_en.gettext
    
    report_dict = await report.dict_with_binary(bot, gettext_func)
    print("__report_dict__",report_dict)
    
    path = pdfGenerator(report_name).generate(report_dict, gettext_func)  # ← ВАЖНО!
    return path



@router.callback_query(F.data == "regenerate_pdf_ru")
async def regenerate_pdf_ru(callback: types.CallbackQuery):
    """Регенерация PDF на русском языке"""
    await callback.answer()
    # Удаляем предыдущее сообщение с кнопкой
    await callback.message.delete()  
    # Получаем экземпляр бота из контекста
    from loader import bot  
    # Генерируем и отправляем PDF на русском
    await send_pdf_report(bot, callback.message, locale="ru")
