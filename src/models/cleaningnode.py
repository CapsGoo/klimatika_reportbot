from typing import BinaryIO
from aiogram import types, Bot
# from aiogram.utils.i18n import lazy_gettext as __

from dataclasses import dataclass, field

from enum import IntEnum

from aiogram.utils.i18n import gettext as _


@dataclass
class CleaningNode:
    class Type(IntEnum):
        UNKNOWN = -1
        DEFAULT = 0
        OTHER = 1

    name: str
    type: Type
    photo_before: types.PhotoSize | None = None
    photo_after: types.PhotoSize | None = None
    button_text: str = ""
    comment: str | None = None
    video_id: types.Video | None = None
    extra_factors: str | None = None

    def __eq__(self, other):
        if not isinstance(other, CleaningNode):
            return False
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.name, self.type))

    def __post_init__(self):
        if not self.button_text:
            self.button_text = self.name


    def create_custom_nodes_list(node_names: list[str]):
        """
        Создает список кастомных узлов обслуживания из списка названий
        Args:
            node_names: Список строк с названиями узлов (например: ["diffuser", "PCB"])
        Returns:
            Список объектов CleaningNode с заданными названиями и типом DEFAULT
        """
        return [
            CleaningNode(
                name=name,
                button_text=name,
                type=CleaningNode.Type.DEFAULT
            )
            for name in node_names
        ]
    
    # def get_custom_nodes_list():
        
    #     data=["diffuser","condenser(outdoor unit)","PCB","insulation","capacitor"]
    #     return data



DEFAULT_INDOOR_SERVICE_NODES = [
    CleaningNode("valve", type=CleaningNode.Type.DEFAULT, button_text=("valve")),
    CleaningNode("аctuator", type=CleaningNode.Type.DEFAULT, button_text=("аctuator")),
    CleaningNode("insulation fixing", type=CleaningNode.Type.DEFAULT, button_text=("insulation fixing")),
    CleaningNode("indoor unit condenser replacement", type=CleaningNode.Type.DEFAULT, button_text=("indoor unit condenser replacement")),
    CleaningNode("thermostat adjustment", type=CleaningNode.Type.DEFAULT, button_text=("thermostat adjustment")),
    CleaningNode("thermostat replacement", type=CleaningNode.Type.DEFAULT, button_text=("thermostat replacement")),
    CleaningNode("motor replacement ", type=CleaningNode.Type.DEFAULT, button_text=("motor replacement")),
    CleaningNode("blower replacement", type=CleaningNode.Type.DEFAULT, button_text=("blower replacement")),
    CleaningNode("filter replacement/installation", type=CleaningNode.Type.DEFAULT, button_text=("filter replacement/installation"))
    ]



DEFAULT_OUTDOOR_SERVICE_NODES = [
    CleaningNode("compressor replacement", type=CleaningNode.Type.DEFAULT, button_text=("compressor replacement")),
    CleaningNode("starter replacement", type=CleaningNode.Type.DEFAULT, button_text=("starter replacement")),
    CleaningNode("motor replacement", type=CleaningNode.Type.DEFAULT, button_text=("motor replacement")),
    CleaningNode("capacitor replacement", type=CleaningNode.Type.DEFAULT, button_text=("capacitor replacement")),
    CleaningNode("fan motor", type=CleaningNode.Type.DEFAULT, button_text=("fan motor")),
    CleaningNode("electrical checking and tightening", type=CleaningNode.Type.DEFAULT, button_text=("electrical checking and tightening")),
    CleaningNode("gas pressure checking", type=CleaningNode.Type.DEFAULT, button_text=("gas pressure checking"))
    ]

DEFAULT_OTHER_SERVICE_NODES = [
    CleaningNode("water heater replacement", type=CleaningNode.Type.DEFAULT, button_text=("water heater replacement")),
    CleaningNode("pump replacement", type=CleaningNode.Type.DEFAULT, button_text=("pump replacement")),
    CleaningNode("FAHU motor replacement", type=CleaningNode.Type.DEFAULT, button_text=("FAHU motor replacement")),
    CleaningNode("FAHU belt replacement", type=CleaningNode.Type.DEFAULT, button_text=("FAHU belt replacement")),
    CleaningNode("high efficiency filter replacement", type=CleaningNode.Type.DEFAULT, button_text=("high efficiency filter replacement"))
    ]

DEFAULT_SERVICE_NODES = [
    CleaningNode("аctuator", type=CleaningNode.Type.DEFAULT),
    CleaningNode("motor", type=CleaningNode.Type.DEFAULT),
    CleaningNode("isolation", type=CleaningNode.Type.DEFAULT),
    CleaningNode("electronic fasteners tightening", type=CleaningNode.Type.DEFAULT),
    CleaningNode("level fixing", type=CleaningNode.Type.DEFAULT),
    CleaningNode("compressor", type=CleaningNode.Type.DEFAULT),
    CleaningNode("capacitor replacement(outside unit)", type=CleaningNode.Type.DEFAULT),
    CleaningNode("fan motor", type=CleaningNode.Type.DEFAULT),
    CleaningNode("fan impeller", type=CleaningNode.Type.DEFAULT)
    ]


DEFAULT_MAINTENANCE_NODES = [
    CleaningNode("grills", type=CleaningNode.Type.DEFAULT, button_text=("grills")),
    CleaningNode("duct", type=CleaningNode.Type.DEFAULT, button_text=("duct")),
    CleaningNode("pan", type=CleaningNode.Type.DEFAULT, button_text=("pan")),
    CleaningNode("evaporator", type=CleaningNode.Type.DEFAULT,button_text=("evaporator")),
    CleaningNode("blower", type=CleaningNode.Type.DEFAULT, button_text=("blower")),
    CleaningNode("filter", type=CleaningNode.Type.DEFAULT, button_text=("filter")),
    CleaningNode("ceiling area", type=CleaningNode.Type.DEFAULT, button_text=("ceiling area"))
    ]

DEFAULT_MAINTENANCE_CUSTOM_NODES = [
    CleaningNode("diffuser", button_text="diffuser", type=CleaningNode.Type.DEFAULT),
    CleaningNode("condenser(outdoor unit)", button_text="condenser(outdoor unit)", type=CleaningNode.Type.DEFAULT),
    CleaningNode("PCB", button_text="PCB", type=CleaningNode.Type.DEFAULT),
    CleaningNode("insulation", button_text="insulation", type=CleaningNode.Type.DEFAULT),
    CleaningNode("capacitor", button_text="capacitor", type=CleaningNode.Type.DEFAULT)
    ]




DEFAULT_FULL_MAINTENANCE_CHECK_LIST_NODE = [
    CleaningNode("Disassembling and cleaning the grills", type=CleaningNode.Type.DEFAULT, button_text="Disassembling and cleaning the grills"),
    CleaningNode("Duct cleaning and desinfection", type=CleaningNode.Type.DEFAULT, button_text="Duct cleaning and desinfection"),
    CleaningNode("Evaporator cleaning and desinfection", type=CleaningNode.Type.DEFAULT, button_text="Evaporator cleaning and desinfection"),
    CleaningNode("Blower cleaning", type=CleaningNode.Type.DEFAULT, button_text="Blower cleaning"),
    CleaningNode("Filter cleaning", type=CleaningNode.Type.DEFAULT, button_text="Filter cleaning"),
    CleaningNode("Installation of additional filters", type=CleaningNode.Type.DEFAULT, button_text="Installation of additional filters"),
    CleaningNode("Drainage cleaning", type=CleaningNode.Type.DEFAULT, button_text="Drainage cleaning"),
    CleaningNode("Outside unit cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text="Outside unit cleaning (if required)"),
    CleaningNode("Pcb cleaning", type=CleaningNode.Type.DEFAULT, button_text="Pcb cleaning"),
    CleaningNode("Pulling electrical fasteners", type=CleaningNode.Type.DEFAULT, button_text="Pulling electrical fasteners")

    ]

DEFAULT_SUPPORT_CHECK_LIST_NODE = [
    CleaningNode("Checking for mold on the grill", type=CleaningNode.Type.DEFAULT, button_text="Checking for mold on the grill"),
    CleaningNode("Duct desinfection", type=CleaningNode.Type.DEFAULT, button_text="Duct desinfection"),
    CleaningNode("Evaporator desinfection", type=CleaningNode.Type.DEFAULT, button_text="Evaporator desinfection"),
    CleaningNode("Filter cleaning", type=CleaningNode.Type.DEFAULT, button_text="Filter cleaning"),
    CleaningNode("Installation of additional filters", type=CleaningNode.Type.DEFAULT, button_text="Installation of additional filters"),
    CleaningNode("Pan cleaning", type=CleaningNode.Type.DEFAULT, button_text="Pan cleaning"),
    CleaningNode("Drainage cleaning", type=CleaningNode.Type.DEFAULT, button_text="Drainage cleaning"),
    CleaningNode("Outside unit cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text="Outside unit cleaning (if required)"),
    CleaningNode("pcb cleaning (if required)", type=CleaningNode.Type.DEFAULT, button_text="pcb cleaning (if required)"),
    CleaningNode("Pulling electrical fasteners (if required)", type=CleaningNode.Type.DEFAULT, button_text="Pulling electrical fasteners (if required)")
    ]

DEFAULT_OTHER_CHECK_LIST_NODE = [
    CleaningNode("Evaporator service Fresh Air Unit(FHU)", type=CleaningNode.Type.DEFAULT, button_text="Evaporator service Fresh Air Unit(FHU)"),
    CleaningNode("Blower service (FHU)", type=CleaningNode.Type.DEFAULT, button_text="Blower service (FHU)"),
    CleaningNode("Filter cleaning (FHU)", type=CleaningNode.Type.DEFAULT, button_text="Filter cleaning (FHU)"),
    CleaningNode("Fine filter (FHU)", type=CleaningNode.Type.DEFAULT, button_text="Fine filter (FHU)"),
    CleaningNode("Belt FHU", type=CleaningNode.Type.DEFAULT, button_text="Belt FHU"),
    CleaningNode("Exhaust fan", type=CleaningNode.Type.DEFAULT, button_text="Exhaust fan")
    ]