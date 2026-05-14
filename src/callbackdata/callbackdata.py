from aiogram.filters.callback_data import CallbackData
from src.models import Report, Client, Room, CleaningNode, Block, Time


class ClientCB(CallbackData, prefix="client"):
    type: Client.Type


class ServiceCB(CallbackData, prefix="service"):
    service: Report.Service


class ExtraServiceCB(CallbackData, prefix="ex_service"):
    action: str
    service: Report.ExtraService


class OtherExtraServiceCB(CallbackData, prefix="oth_ex_service"):
    action: str
    id: int


class RoomTypeCB(CallbackData, prefix="room"):
    type: Room.Type

class BlockTypeCB(CallbackData, prefix="block"):
    type: Block.Type

class TimeTypeCB(CallbackData, prefix="time"):
    type: Time.Type
    

class CleaningNodeCB(CallbackData, prefix="cleaning_node"):
    action: str  # "add", "delete", "add_other", "enter", "page"
    index: int 
    type: CleaningNode.Type
    page: int = 1  # Добавляем параметр страницы
    

class FactorCB(CallbackData, prefix="factor"):
    # action: str
    # factor: Report.Factor
    # index: int
    type: Report.Type

class MasterCB(CallbackData, prefix="master"):
    name: str 

class IncompleteNodeCB(CallbackData, prefix="incomplete_node"):
    # room_type: str
    node_name: str
    missing_type: str  # Now can be: photo:'p', video:'v', comment:'c', master:'m' or combinations with '_'


class NodeActionCB(CallbackData, prefix="node_action"):
    action: str  # 'add_p' или 'add_c' или 'add_v' или 'add_m'
    # room_type: str
    node_name: str


class CheckListNodeCB(CallbackData, prefix="check_list"):
    action: str  # "add", "delete", "add_other", "enter", "page"
    index: int 
    type: CleaningNode.Type
    node_name: str

    